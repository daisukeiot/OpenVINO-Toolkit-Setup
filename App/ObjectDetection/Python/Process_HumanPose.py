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
# 19 Key Part Locations
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

# pairs of key Point Locations
CocoPairs = [
    (1, 2),   # Neck - RShoulder
    (1, 5),   # Neck - LShoulder
    (2, 3),   # RShoulder - RElbow
    (3, 4),   # RElbow - RWrist
    (5, 6),   # LShoulder - LElbow
    (6, 7),   # LElbow - LWrist
    (1, 8),   # Neck - RHip
    (8, 9),   # RHip - RKnee
    (9, 10),  # RKnee - RAnkle
    (1, 11),  # Neck - LHip
    (11, 12), # LHip - LKnee
    (12, 13), # LKnee - LAnkle
    (1, 0),   # Neck - Nose
    (0, 14),  # Nose - REye
    (14, 16), # REye - REar
    (0, 15),  # Nose - LEye
    (15, 17), # LEye - LEar
    (2, 16),  # RShoulder - REar
    (5, 17)   # LShoulder - LEar
]   # = 19

# blob locations for each pair
CocoPairsNetwork = [
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

# Color for each Key Point Location
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

class Human_Pose_Processor():

    def __init__(self, model_name, input_format, input_shape, input_layout):
        logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        self.model_name = model_name
        self.input_format = input_format

        self.input_key = 'data'
        self.input_shape = input_shape
        self.input_layout = input_layout

        self.paf_key  = 'Mconv7_stage2_L1'
        self.bpl_key = 'Mconv7_stage2_L2'

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
        pafs   = results[self.paf_key][0, :, :, :]

        # key part, height, width
        bpls  = results[self.bpl_key][0, :, :, :]
        
        # Flat list with index (J)
        # x, y, confidence score, index
        # S = (S1, S2, ..., SJ)
        # bpl_List = ((x,y,score,0),
        #                  :
        #             (x,y,score,bpl_J))
        #
        bpl_List = []

        #
        # array of key points
        # [# of key points][x, y, score]
        # bpl_Array[bpl_j](x, y, score)
        bpl_Array = np.zeros((0,3))

        #
        # array organized key points by key points
        # [SJ][x,y,score,index]
        # [nose][x, y, score, index]
        bpl_by_J = []

        bpl_List, bpl_Array, bpl_by_J = self.process_bpl(results, frame)
        
        bpl_pairs = self.find_bpl_pairs(results, bpl_by_J, frame, confidence)
        
        bpl_k = self.assign_bpl_to_person(bpl_pairs)

        return self.draw_person(bpl_k, bpl_List, frame)

    def draw_person(self, bpl_k, bpl_List, frame):

        for k in range(len(bpl_k)):
            logging.debug(bpl_k[k])

            # exclude persons without Neck
            if bpl_k[k][1] == -1:
                continue

            for i in range(len(CocoPairs) -2 ):
                if bpl_k[k][CocoPairs[i][0]] == -1 or bpl_k[k][CocoPairs[i][1]] == -1:
                    continue
                bpl_0 = int(bpl_k[k][CocoPairs[i][0]])
                bpl_1 = int(bpl_k[k][CocoPairs[i][1]])
                loc_0 = bpl_List[bpl_0]
                loc_1 = bpl_List[bpl_1]

                cv2.line(frame, (loc_0[0], loc_0[1]), (loc_1[0], loc_1[1]), CocoColors[i], 1.5, cv2.LINE_AA)

        return frame
        
    def assign_bpl_to_person(self, bpl_pairs):

        # Identify key point pairs for each person

        # per person bpl pairs
        bpl_k = -1 * np.ones((0, 19))

        # We don't need Shoulder - Ear pairs
        for i in range(len(CocoPairs) - 2):
            if len(bpl_pairs[i]) == 0:
                continue

            bpl_0 = bpl_pairs[i][:,0]
            bpl_1 = bpl_pairs[i][:,1]

            bpl_index_0, bpl_index_1 = CocoPairs[i]

            # loop through pairs for each body part
            for j in range(len(bpl_pairs[i])):
                found = False
                person_index = -1

                for k in range(len(bpl_k)):
                    if bpl_k[k][bpl_index_0] == bpl_0[j]:
                        person_index = k
                        found = True
                        break

                if found:
                    bpl_k[person_index][bpl_index_1] = bpl_1[j]
                else:
                    # create a new list for person K
                    pair_k = -1 * np.ones(19)
                    pair_k[bpl_index_0] = bpl_0[j]
                    pair_k[bpl_index_1] = bpl_1[j]
                    bpl_k = np.vstack([bpl_k, pair_k])    
    
        return bpl_k

    def find_bpl_pairs(self, results, bpl_by_J, frame, confidence):
        #
        # Process PAF
        # Find         
        bpl_pairs = []

        # We don't need Shoulder - Ear pairs
        for i in range(len(CocoPairsNetwork) - 2):

            paf_0 = results[self.paf_key][0, CocoPairsNetwork[i][0], :, :]
            paf_1 = results[self.paf_key][0, CocoPairsNetwork[i][1], :, :]

            paf_0 = cv2.resize(paf_0, (frame.shape[1], frame.shape[0]))
            paf_1 = cv2.resize(paf_1, (frame.shape[1], frame.shape[0]))

            keyP_0 = bpl_by_J[CocoPairs[i][0]]
            keyP_1 = bpl_by_J[CocoPairs[i][1]]

            if len(keyP_0) == 0 or len(keyP_1) == 0:
                bpl_pairs.append([])
                continue

            bpl_pair = np.zeros((0,3))

            for j in range(len(keyP_0)):

                maxScore = -1
                max_k = -1
                found = False

                for k in range(len(keyP_1)):
                    # dj2 - dj1
                    distance = np.subtract(keyP_1[k][:2], keyP_0[j][:2])

                    # || dj2 - dj1 ||2
                    norm = np.linalg.norm(distance)

                    if norm:
                        # (dj2 - dj1)/(|| dj2 - dj1 ||2)
                        vector = distance / norm
                    else:
                        continue

                    # p(u)
                    interp_coord = list(zip(np.linspace(keyP_0[j][0], keyP_1[k][0], num=10),
                                            np.linspace(keyP_0[j][1], keyP_1[k][1], num=10)))

                    paf_interp = []
                    for l in range(len(interp_coord)):
                        paf_interp.append([paf_0[int(round(interp_coord[l][1])), int(round(interp_coord[l][0]))],
                                           paf_1[int(round(interp_coord[l][1])), int(round(interp_coord[l][0]))] ])

                    # L(p(u)) dot vector
                    paf_scores = np.dot(paf_interp, vector)
                    # E
                    avg_paf_score = sum(paf_scores)/len(paf_scores)

                    if avg_paf_score > confidence and ( len(np.where(paf_scores > 0.1)[0]) / 10 ) > 0.5 :
                        if avg_paf_score > maxScore:
                            max_k = k
                            maxScore = avg_paf_score
                            found = True

                if found:
                    bpl_pair = np.append(bpl_pair, [[int(keyP_0[j][3]), int(keyP_1[max_k][3]), maxScore]], axis=0)

            bpl_pairs.append(bpl_pair)
        
        return bpl_pairs
        
    def process_bpl(self, results, frame):
        #
        # Process Body Part Locations
        #
        # 3.3 Confidence Maps for Part Detection
        # Each confidence map is a 2D representation of the belief that a particular body part can be 
        # located in any given pixel. 
        # Ideally, if a single person appears in the image, a single peak should exist in each confidence map
        # if the corresponding part is visible; if multiple people are in the image, there should be a peak
        # corresponding to each visible part j for each person k.
        #

        # Index for each Body Part Location in j
        bpl_index = 0

        # Flat list with index (J)
        # x, y, confidence score, index
        # S = (S1, S2, ..., SJ)
        # bpl_List = ((x,y,score,0),
        #                  :
        #             (x,y,score,bpl_J))
        #
        bpl_List = []

        #
        # array of key points
        # [# of key points][x, y, score]
        # bpl_Array[bpl_j](x, y, score)
        bpl_Array = np.zeros((0,3))

        #
        # array organized key points by key points
        # [SJ][x,y,score,index]
        # [nose][x, y, score, index]
        bpl_by_J = []

        keypoint_list_by_part_id = []

        # Loop each Body Part Location, except Background
        for J in range(CocoPart.Background.value):

            logging.debug('>> Process {}'.format(CocoPart(J).name))

            #
            # Confidence Map or "S"
            # 3.3 Confidence Maps for Part Detection
            #
            bpl_ConfMap_j = results[self.bpl_key][0, J, :, :]
            
            # Use Non-NMS method (Faster)
            # bodyPartList = find_key_points_nms(bpl_ConfMap_j, frame)
            bodyPartList = find_key_points(bpl_ConfMap_j, frame)

            tmpList = []

            for bodyPart in bodyPartList:
                # Create a list of keypoints with index for display
                logging.debug('   - Index {} : ({},{}) {:.2f}%'.format(bpl_index, 
                                                           bodyPart[0],
                                                           bodyPart[1],
                                                           bodyPart[2]))
                #
                # tempList = (x, y), score, index
                #

                # add to flat list
                bpl_List.append(bodyPart + (bpl_index,))

                # add to temp list (list by J)
                tmpList.append(bodyPart + (bpl_index,))
                bpl_index += 1

                # add to array
                bpl_Array = np.vstack([bpl_Array, bodyPart])

            bpl_by_J.append(tmpList)

        #
        # for debugging
        # display_bpl_heatmap(results, self.bpl_key, bpl_by_J, frame)f
        return bpl_List, bpl_Array, bpl_by_J

def find_key_points(confidence_map, frame):
    #
    # find Body Part Locations using Contours and MaxLoc
    # Returns list of Body Part Locations with Confidence Score
    #

    # Resize and smooth the Body Part Location Confidence Map (J)
    bpl_ConfMap_j = cv2.resize(confidence_map, (frame.shape[1], frame.shape[0]))
    bpl_ConfMap_Blur = cv2.GaussianBlur(bpl_ConfMap_j, (3,3), 0, 0)

    # filter low probability ones (< 0.1)
    bpl_ConfMap_Filter = np.uint8(bpl_ConfMap_Blur > 0.1)

    bodyPartList = []

    # find contours (or rectangles)
    contours, _ = cv2.findContours(bpl_ConfMap_Filter, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) != 0:

        for contour in contours:
            tmp = np.zeros(bpl_ConfMap_Filter.shape)
            tmp = cv2.fillConvexPoly(tmp, contour, 1)

            weighted_bpl_ConfMap = bpl_ConfMap_Blur * tmp

            # We take the maximum of the confidence maps instead of
            # the average so that the precision of nearby peaks remains distinct
            _, maxVal, _, maxLoc = cv2.minMaxLoc(weighted_bpl_ConfMap)

            tmp = maxLoc + (bpl_ConfMap_j[maxLoc[1], maxLoc[0]],)
            bodyPartList.append(maxLoc + (bpl_ConfMap_j[maxLoc[1], maxLoc[0]],))

    return bodyPartList

from scipy.ndimage.filters import maximum_filter

def find_key_points_nms(confidence_map, frame):
    #
    # find Body Part Locations using Non Maximum Suppression
    # Returns list of Body Part Locations with Confidence Score
    # This is slower

    bodyPartList = []

    bpl_ConfMap_j = cv2.resize(confidence_map, (frame.shape[1], frame.shape[0]))
    bpl_ConfMap_Blur = cv2.GaussianBlur(bpl_ConfMap_j, (3,3), 0, 0)

    bpl_ConfMap_Blur[bpl_ConfMap_Blur < 0] = 0

    part_candidates = bpl_ConfMap_Blur*(bpl_ConfMap_Blur == maximum_filter(bpl_ConfMap_Blur, footprint=np.ones((3, 3))))
    tmp = np.where(part_candidates >= 0.1)

    for i in range(len(tmp[0])):
        bodyPartList.append((tmp[1][i], tmp[0][i]) + (bpl_ConfMap_j[tmp[0][i], tmp[1][i]],))

    return bodyPartList