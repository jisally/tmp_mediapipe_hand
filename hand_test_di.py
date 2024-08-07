import os
import json
import cv2
import mediapipe as mp

# Mediapipe Hands 모듈 로드
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# 트랙바 이벤트 핸들러 함수
def onChange(pos):
    cap.set(cv2.CAP_PROP_POS_FRAMES, pos)

# 비디오에서 손을 감지하는 함수
def detect_hands_in_video(video_path, output_dir):
    landmarks_data_left = [[] for _ in range(21)]  # 21개의 랜드마크를 가집니다.
    landmarks_data_right = [[] for _ in range(21)]  # 21개의 랜드마크를 가집니다.

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cv2.namedWindow('MediaPipe Hands')
    cv2.createTrackbar('Position', 'MediaPipe Hands', 0, total_frames, onChange)

    with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_hands=2) as hands:
        while cap.isOpened():
            position = cv2.getTrackbarPos('Position', 'MediaPipe Hands')
            cap.set(cv2.CAP_PROP_POS_FRAMES, position)
            ret, frame = cap.read()
            if not ret:
                break

            # BGR 이미지를 RGB로 변환합니다.
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 이미지를 처리하고 손 랜드마크를 찾습니다.
            results = hands.process(image)

            # 이미지에 손 랜드마크를 그립니다.
            if results.multi_hand_landmarks:
                hands_count = len(results.multi_hand_landmarks)
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                for id in range(21):  # 각 랜드마크에 대해
                    if hands_count == 2:
                        # 두 손이 감지된 경우
                        if results.multi_hand_landmarks[0].landmark[0].x > results.multi_hand_landmarks[1].landmark[0].x:
                            left_hand = results.multi_hand_landmarks[0]
                            right_hand = results.multi_hand_landmarks[1]
                        else:
                            left_hand = results.multi_hand_landmarks[1]
                            right_hand = results.multi_hand_landmarks[0]
                            
                        coordinate_left = [left_hand.landmark[id].x, left_hand.landmark[id].y, left_hand.landmark[id].z]
                        coordinate_right = [right_hand.landmark[id].x, right_hand.landmark[id].y, right_hand.landmark[id].z]
                        landmarks_data_left[id].append(coordinate_left)
                        landmarks_data_right[id].append(coordinate_right)
                        
                    elif hands_count == 1:  
                        # 한 손만 감지된 경우
                        if results.multi_hand_landmarks[0].landmark[4].x < results.multi_hand_landmarks[0].landmark[20].x:
                            coordinate_right = [results.multi_hand_landmarks[0].landmark[id].x, results.multi_hand_landmarks[0].landmark[id].y, results.multi_hand_landmarks[0].landmark[id].z]
                            landmarks_data_right[id].append(coordinate_right)
                            landmarks_data_left[id].append([])
                        else:
                            coordinate_left = [results.multi_hand_landmarks[0].landmark[id].x, results.multi_hand_landmarks[0].landmark[id].y, results.multi_hand_landmarks[0].landmark[id].z]
                            landmarks_data_left[id].append(coordinate_left)
                            landmarks_data_right[id].append([])
                            
                    else: 
                        # 손이 감지되지 않은 경우
                        landmarks_data_left[id].append([])
                        landmarks_data_right[id].append([])
                        
            else:  # 손이 감지되지 않은 경우
                for id in range(21):
                    landmarks_data_left[id].append([])
                    landmarks_data_right[id].append([])

            cv2.imshow('MediaPipe Hands', frame)
            cv2.setTrackbarPos('Position', 'MediaPipe Hands', int(cap.get(cv2.CAP_PROP_POS_FRAMES)))
            if cv2.waitKey(5) & 0xFF == 27:
                break

    # JSON 파일로 데이터를 저장합니다.
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_folder = os.path.join(output_dir, video_name)
    os.makedirs(output_folder, exist_ok=True)

    for id, data in enumerate(landmarks_data_left):
        with open(os.path.join(output_folder, f'landmarks_data_left_{id}.json'), 'w') as f:
            json.dump(data, f)

    for id, data in enumerate(landmarks_data_right):
        with open(os.path.join(output_folder, f'landmarks_data_right_{id}.json'), 'w') as f:
            json.dump(data, f)

    cv2.destroyAllWindows()
    cap.release()

# '001' 폴더 안의 모든 mp4 파일 처리
input_dir = 'C:/Users/seungyeon0510/Desktop/jjii/001'
output_dir = 'C:/Users/seungyeon0510/Desktop/jjii/mediapiejson'

for filename in os.listdir(input_dir):
    if filename.endswith('.mp4'):
        video_path = os.path.join(input_dir, filename)
        detect_hands_in_video(video_path, output_dir)
