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
