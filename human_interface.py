import cv2 as cv
import gym


##Enums:
LEFT = 0
STRAIGHT = 1
RIGHT = 2
SHOOT = 3
actions = {52: LEFT, 56: STRAIGHT, 53: STRAIGHT, 54: RIGHT, 48: SHOOT}
actions_names = {52: 'LEFT', 56: 'STRAIGHT', 53: 'STRAIGHT', 54: 'RIGHT', 48: 'SHOOT'}


def main():
    env = gym.make('interceptor-v0')
    state = env.reset()
    for i in range(1000):
        im = env.render('human')
        im = cv.resize(im.astype("uint8"), (int(im.shape[0] / 5), int(im.shape[1] / 5)))
        cv.imshow("4-left, 5-straight, 6-right, 0-shoot", im)
        key = cv.waitKey()
        action = STRAIGHT
        if key in actions.keys():
            action = actions[key]
            action_name = actions_names[key]

        state, reward, done, info = env.step(action)
        print("Step: " + str(i) + ", action: " + action_name + ", step reward: " + str(reward) + ", game score: " + str(info["game score"]) + ", rockets: " + str(info["rockets"]) )
        if done:
            break


if __name__ == '__main__':
    main()
