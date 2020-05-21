import sys
import logging
import traceback
from enum import Enum
import math
import numpy as np
import cv2
import matplotlib.pyplot as plt
from scipy.ndimage.filters import maximum_filter
from collections import defaultdict
import itertools

from OpenVINO_Config import Output_Format, Input_Format, color_list, CV2_Draw_Info

#
# For Human Pose models
#

class CocoPart(Enum):
    Nose = 0
    Neck = 1
    RShoulder = 2
    RElbow = 3
    RWrist = 4
    LShoulder = 5
    LElbow = 6
    LWrist = 7
    RHip = 8
    RKnee = 9
    RAnkle = 10
    LHip = 11
    LKnee = 12
    LAnkle = 13
    REye = 14
    LEye = 15
    REar = 16
    LEar = 17
    Background = 18

CocoPairs = [
    (1, 2),
    (1, 5),
    (2, 3),
    (3, 4),
    (5, 6),
    (6, 7),
    (1, 8),
    (8, 9),
    (9, 10),
    (1, 11),
    (11, 12),
    (12, 13),
    (1, 0),
    (0, 14),
    (14, 16),
    (0, 15),
    (15, 17),
    (2, 16),
    (5, 17)
]   # = 19

CocoPairsRender = CocoPairs[:-2]


CocoPairsBlobIndex = [
    (12, 13),
    (20, 21),
    (14, 15),
    (16, 17),
    (22, 23),
    (24, 25),
    (0, 1),
    (2, 3),
    (4, 5),
    (6, 7),
    (8, 9),
    (10, 11),
    (28, 29),
    (30, 31),
    (34, 35),
    (32, 33),
    (36, 37),
    (18, 19),
    (26, 27)
 ]  # = 19

# In BGR
CocoColors = [[  0,   0, 255], #nose
              [102,  51, 204], #neck
              [255,   0,   0], #R Shoulder
              [255, 153,   0], #R Elbow
              [255, 204, 153], #R Wrist
              [  0, 255,   0], #L Shoulder
              [153, 255,   0], #L Elbow
              [153, 255, 204], #L Wrist
              [255,   0,   0], #R Hip
              [255,   0,   0], #R Knee
              [255,   0,   0], #R Ankle
              [  0, 255,   0], #L Hip
              [  0, 255,   0], #L Knee
              [  0, 255,   0], #L Ankle
              [  0, 255, 255], #R Eye
              [  0, 255, 255], #L Eye
              [255,   0, 255], #R Ear
              [255,   0, 255]] #L Ear

#
# Flat list with index
# x, y, score, index
list_keypoint_with_index = []

#
# array of key points
# [# of key points][x, y, score]
array_keypoint = np.zeros((0,3))

#
# array organized key points by key points
# [nose][x, y, score, index]
array_keypoint_by_part_id = []

key_point_confidence = 0.1
confidence = 0.3

class Human_Pose_Processor():

    def __init__(self, model_name, input_format, input_shape, input_layout):
        logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        self.model_name = model_name
        self.input_format = input_format

        self.input_key = 'data'
        self.input_shape = input_shape
        self.input_layout = input_layout

        self.paf_key  = 'Mconv7_stage2_L1'
        self.keyP_key = 'Mconv7_stage2_L2'

        self.key_point_confidence = 0.1
        self.draw_key_point_id = True

    def process_for_inference(self, frame):

        frame_data = np.array([])

        if self.input_layout == 'NCHW':
            n, c, h, w = self.input_shape
            # resize based on shape
            frame_data = cv2.resize(frame, (w, h))
            # convert from H,W,C to C,H,W
            frame_data = frame_data.transpose((2,0,1))
            # convert to C,H,W to N,C,H,W
            frame_data = frame_data.reshape(self.input_shape)

        return frame_data, self.input_key

    def process_result(self, results = None, frame = None, confidence = 1):

        # paf, height, width
        pafMat   = results[self.paf_key][0, :, :, :]

        # key part, height, width
        keyP_HeatMap  = results[self.keyP_key][0, :, :, :]

        frame = self.process_key_points(frame, keyP_HeatMap)

        # humans = self.estimate_pose(heatMat, pafMat, confidence)

        # frame = self.draw_humans(frame, humans)

        return frame

    def process_key_points(self, frame, result):

        keyP_id = 0

        #
        # Flat list with index
        # x, y, score, index
        list_keypoint_with_index = []

        #
        # array of key points
        # [# of key points][x, y, score]
        array_keypoint = np.zeros((0,3))

        #
        # array organized key points by key points
        # [nose][x, y, score, index]
        array_keypoint_by_part_id = []

        # iterate through each key point
        for i in range(CocoPart.Background.value):

            keyP_HeatMap = result[i,:,:]
            keyP_HeatMap = cv2.resize(keyP_HeatMap, (frame.shape[1], frame.shape[0]))

            # Smooth key point heatmap with Gaussian Blur
            KeyP_HeatMap_Blue = cv2.GaussianBlur(keyP_HeatMap,(5,5), 0, 0)

            # Mask off anything below threshold
            KeyP_HeatMap_Masked = np.uint8(KeyP_HeatMap_Blue > self.key_point_confidence)

            keypoint_list = []

            #find the blobs
            contours, _ = cv2.findContours(KeyP_HeatMap_Masked, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:

                # placeholder
                keyP_blob = np.zeros(KeyP_HeatMap_Masked.shape)

                # Draw Contour to blob
                keyP_blob = cv2.fillConvexPoly(keyP_blob, contour, 1)

                # Give weight based on Key Point Heatmap Score
                keyP_HeatMap_Weighted = KeyP_HeatMap_Blue * keyP_blob

                # Take max point and location
                _, maxVal, _, maxLoc = cv2.minMaxLoc(keyP_HeatMap_Weighted)
            
                # Add to the list with location.  Take score from the original heatmap
                keypoint_list.append(maxLoc + (keyP_HeatMap[maxLoc[1], maxLoc[0]],))

            # create a list by giving ID to each key point
            tmpList = []

            # iterate each keypoint we found so far and give ID (keyP_id)
            for j in range(len(keypoint_list)):
                # add to temporary list
                tmpList.append(keypoint_list[j] + (keyP_id,))

                # add this to array by id.
                # this list is convenient to iterate all key points.
                # this list looks like :
                # array_keypoint[0][x,y,score]
                array_keypoint = np.vstack([array_keypoint, keypoint_list[j]])
                keyP_id += 1

            # add list of key points by key part to the list head
            #
            # This list looks like :
            # list_keypoint_with_index[key point][(x,y,score,id)]
            # e.g.
            # list_keypoint_with_index[0 (nose)][(x,y,score,id)]
            #
            list_keypoint_with_index.append(tmpList)

        frame = self.draw_key_points(frame, list_keypoint_with_index)

        return frame

    def draw_key_points(self, frame, list_keypoint_with_index):

        # to draw key points with ID use list_keypoint_with_index

        for i in range(len(list_keypoint_with_index)):
            if len(list_keypoint_with_index[i]) == 0:
                continue

            for keyP in list_keypoint_with_index[i]:
                if keyP[2] > self.key_point_confidence:
                    x = int(keyP[0])
                    y = int(keyP[1])
                    if self.draw_key_point_id == True:
                        frame = cv2.putText(frame, str(i), (x + 4,y + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.3, CocoColors[i], 1, cv2.LINE_AA)

                    frame = cv2.circle(frame, (x, y), 3, CocoColors[i], -1, cv2.LINE_AA)

        return frame

    # def draw_humans(self, img, human_list):
    #     img_copied = np.copy(img)
    #     image_h, image_w = img_copied.shape[:2]
    #     offset_y =(image_h / 32 ) /2
    #     offset_x =(image_w / 57 ) /2
    #     centers = {}
    #     for human in human_list:
    #         part_idxs = human.keys()

    #         # draw point
    #         for i in range(CocoPart.Background.value):
    #             if i not in part_idxs:
    #                 continue
    #             part_coord = human[i][1]
    #             center = (int(part_coord[0] * image_w + offset_x), int(part_coord[1] * image_h + offset_y))
    #             centers[i] = center
    #             cv2.circle(img_copied, center, 3, CocoColors[i], thickness=2, lineType=8, shift=0)

    #         # draw line
    #         for pair_order, pair in enumerate(CocoPairsRender):
    #             if pair[0] not in part_idxs or pair[1] not in part_idxs:
    #                 continue

    #             img_copied = cv2.line(img_copied, centers[pair[0]], centers[pair[1]], CocoColors[pair_order], 2)

    #     return img_copied

    # def human_conns_to_human_parts(self, human_conns, heatMat):
    #     human_parts = defaultdict(lambda: None)
    #     for conn in human_conns:
    #         human_parts[conn['partIdx'][0]] = (
    #             conn['partIdx'][0], # part index
    #             (conn['coord_p1'][0] / heatMat.shape[2], conn['coord_p1'][1] / heatMat.shape[1]), # relative coordinates
    #             heatMat[conn['partIdx'][0], conn['coord_p1'][1], conn['coord_p1'][0]] # score
    #             )
    #         human_parts[conn['partIdx'][1]] = (
    #             conn['partIdx'][1],
    #             (conn['coord_p2'][0] / heatMat.shape[2], conn['coord_p2'][1] / heatMat.shape[1]),
    #             heatMat[conn['partIdx'][1], conn['coord_p2'][1], conn['coord_p2'][0]]
    #             )
    #     return human_parts

    # def get_score(self, x1, y1, x2, y2, pafMatX, pafMatY):
    #     num_inter = 10
    #     dx, dy = x2 - x1, y2 - y1
    #     normVec = math.sqrt(dx ** 2 + dy ** 2)

    #     if normVec < 1e-4:
    #         return 0.0, 0

    #     vx, vy = dx / normVec, dy / normVec

    #     xs = np.arange(x1, x2, dx / num_inter) if x1 != x2 else np.full((num_inter, ), x1)
    #     ys = np.arange(y1, y2, dy / num_inter) if y1 != y2 else np.full((num_inter, ), y1)
    #     xs = (xs + 0.5).astype(np.int8)
    #     ys = (ys + 0.5).astype(np.int8)

    #     # without vectorization
    #     pafXs = np.zeros(num_inter)
    #     pafYs = np.zeros(num_inter)
    #     for idx, (mx, my) in enumerate(zip(xs, ys)):
    #         pafXs[idx] = pafMatX[my][mx]
    #         pafYs[idx] = pafMatY[my][mx]

    #     # vectorization slow?
    #     # pafXs = pafMatX[ys, xs]
    #     # pafYs = pafMatY[ys, xs]

    #     local_scores = pafXs * vx + pafYs * vy
    #     thidxs = local_scores > Inter_Threashold

    #     return sum(local_scores * thidxs), sum(thidxs)

    # def non_max_suppression(self, heatmap, window_size=3, threshold=NMS_Threshold):
    #     heatmap[heatmap < threshold] = 0 # set low values to 0
    #     part_candidates = heatmap*(heatmap == maximum_filter(heatmap, footprint=np.ones((window_size, window_size))))
    #     return part_candidates

    # def estimate_pose(self, heatMat, pafMat, Confidence):

    #     NMS_Threshold = Confidence
    #     # reliability issue.
    #     # heatMat = heatMat - heatMat.min(axis=1).min(axis=1).reshape(19, 1, 1)
    #     # heatMat = heatMat - heatMat.min(axis=2).reshape(19, heatMat.shape[1], 1)

    #     _NMS_Threshold = max(np.average(heatMat) * 4.0, NMS_Threshold)
    #     _NMS_Threshold = min(_NMS_Threshold, 0.6)

    #     coords = [] # for each part index, it stores coordinates of candidates
    #     for heatmap in heatMat[:-1]: # remove background
    #         part_candidates = self.non_max_suppression(heatmap, 5, NMS_Threshold)
    #         # coords.append(np.where(part_candidates >= _NMS_Threshold))
    #         coords.append(np.where(part_candidates >= Confidence))

    #     connection_all = [] # all connections detected. no information about what humans they belong to
    #     for (idx1, idx2), (paf_x_idx, paf_y_idx) in zip(CocoPairs, CocoPairsNetwork):
    #         connection = self.estimate_pose_pair(coords, idx1, idx2, pafMat[paf_x_idx], pafMat[paf_y_idx])
    #         connection_all.extend(connection)

    #     conns_by_human = dict()
    #     for idx, c in enumerate(connection_all):
    #         conns_by_human['human_%d' % idx] = [c] # at first, all connections belong to different humans

    #     no_merge_cache = defaultdict(list)
    #     empty_set = set()
    #     while True:
    #         is_merged = False
    #         for h1, h2 in itertools.combinations(conns_by_human.keys(), 2):
    #             if h1 == h2:
    #                 continue
    #             if h2 in no_merge_cache[h1]:
    #                 continue
    #             for c1, c2 in itertools.product(conns_by_human[h1], conns_by_human[h2]):
    #                 # if two humans share a part (same part idx and coordinates), merge those humans
    #                 if set(c1['uPartIdx']) & set(c2['uPartIdx']) != empty_set:
    #                     is_merged = True
    #                     # extend human1 connectios with human2 connections
    #                     conns_by_human[h1].extend(conns_by_human[h2])
    #                     conns_by_human.pop(h2) # delete human2
    #                     break
    #             if is_merged:
    #                 no_merge_cache.pop(h1, None)
    #                 break
    #             else:
    #                 no_merge_cache[h1].append(h2)

    #         if not is_merged: # if no more mergings are possible, then break
    #             break

    #     # reject by subset count
    #     conns_by_human = {h: conns for (h, conns) in conns_by_human.items() if len(conns) >= Min_Subset_Cnt}
    #     # reject by subset max score
    #     conns_by_human = {h: conns for (h, conns) in conns_by_human.items() if max([conn['score'] for conn in conns]) >= Min_Subset_Score}

    #     # list of humans
    #     humans = [self.human_conns_to_human_parts(human_conns, heatMat) for human_conns in conns_by_human.values()]
    #     return humans


    # def estimate_pose_pair(self, coords, partIdx1, partIdx2, pafMatX, pafMatY):
    #     connection_temp = [] # all possible connections
    #     peak_coord1, peak_coord2 = coords[partIdx1], coords[partIdx2]

    #     for idx1, (y1, x1) in enumerate(zip(peak_coord1[0], peak_coord1[1])):
    #         for idx2, (y2, x2) in enumerate(zip(peak_coord2[0], peak_coord2[1])):
    #             score, count = self.get_score(x1, y1, x2, y2, pafMatX, pafMatY)
    #             if (partIdx1, partIdx2) in [(2, 3), (3, 4), (5, 6), (6, 7)]: # arms
    #                 if count < InterMinAbove_Threshold // 2 or score <= 0.0:
    #                     continue
    #             elif count < InterMinAbove_Threshold or score <= 0.0:
    #                 continue
    #             connection_temp.append({
    #                 'score': score,
    #                 'coord_p1': (x1, y1),
    #                 'coord_p2': (x2, y2),
    #                 'idx': (idx1, idx2), # connection candidate identifier
    #                 'partIdx': (partIdx1, partIdx2),
    #                 'uPartIdx': ('{}-{}-{}'.format(x1, y1, partIdx1), '{}-{}-{}'.format(x2, y2, partIdx2))
    #             })

    #     connection = []
    #     used_idx1, used_idx2 = [], []
    #     # sort possible connections by score, from maximum to minimum
    #     for conn_candidate in sorted(connection_temp, key=lambda x: x['score'], reverse=True):
    #         # check not connected
    #         if conn_candidate['idx'][0] in used_idx1 or conn_candidate['idx'][1] in used_idx2:
    #             continue
    #         connection.append(conn_candidate)
    #         used_idx1.append(conn_candidate['idx'][0])
    #         used_idx2.append(conn_candidate['idx'][1])

    #     return connection
