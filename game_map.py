import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt


GREEN = (0, 255, 0)
CITY_COLORS = np.asarray([(0, 0, 255), (255, 0, 0), (0, 128, 128), (128, 0, 128), (128, 128, 0), (0, 0, 64), (0, 64, 0), (64, 0, 0), (0, 64, 64), (64, 0, 64), (64, 64, 0), (0, 0, 32), (0, 32, 0), (32, 0, 0), (0, 32, 32), (32, 0, 32), (32, 32, 0)]).astype("uint8")
FIELD_COLORS = np.ceil(np.asarray(CITY_COLORS)/16).astype("uint8")


def ang2coord(ang):
    res = (np.floor(ang + 90) / 6).astype(int)
    # print("ang: " + str(ang) + " to " + str(res))
    return res


def build_game_map(rockets_list, cur_ang, cur_time):
    disp = False # True #
    max_time = 400
    max_range = 10000
    angs_options = 31
    game_map = np.zeros((max_time+1, angs_options, 3))
    inter_ranges_map = np.zeros((max_time, angs_options)) + max_range
    #inter_ranges_map[0, ang2coord(cur_ang)] = 0
    temp_game_map = np.zeros((max_time, angs_options))
    temp_inter_ranges_map = np.zeros((max_time, angs_options))

    for rocket in rockets_list:
        id = rocket.id
        if rocket.city_hit:
            COLOR = CITY_COLORS[id % len(CITY_COLORS)]
        else:
            COLOR = FIELD_COLORS[id % len(FIELD_COLORS)]

        ## fast version:
        if len(rocket.interception_points) == 0:
            #print("warning: rocket without interceptions. ")
            #print("rocket id: " + str(rocket.id))
            #print("rocket track: " + str(rocket.path))
            continue
        t_and_ang = np.asarray(rocket.interception_points)
        ##init temp data structures:
        temp_game_map[:] = 0
        temp_inter_ranges_map[:] = max_range

        ##remove past times:
        t_and_ang[:, 0] -= cur_time
        t_and_ang = t_and_ang[t_and_ang[:, 0] >= 0]
        t_and_ang = t_and_ang[t_and_ang[:, 0] < max_time]

        ##build temp maps for current track:
        angs = ang2coord(t_and_ang[:, 1])
        temp_game_map[t_and_ang[:, 0], angs] = 1
        temp_inter_ranges_map[t_and_ang[:, 0], angs] = t_and_ang[:, 2]

        ## choose right update for each cell:
        closest_inter = np.argmin(np.dstack((inter_ranges_map, temp_inter_ranges_map)), 2)
        chosen = [closest_inter == 1]
        inter_ranges_map[tuple(chosen)] = temp_inter_ranges_map[tuple(chosen)]
        for i in range(3):
            game_map_i = game_map[:, :, i]
            # game_map_i[chosen] = temp_game_map[chosen] * COLOR[i]
            game_map_i[1:][tuple(chosen)] = temp_game_map[tuple(chosen)] * COLOR[i]
            game_map[:, :, i] = game_map_i
        a=1

    game_map[0, :, :] = 0
    print("actor location: " + str(ang2coord(cur_ang)))
    game_map[0, ang2coord(cur_ang), :] = GREEN

    if disp:
        im = game_map.astype("uint8")
        im = cv.resize(im, (angs_options*40, max_time*3), interpolation=cv.INTER_NEAREST)
        im = 255 - im
        im = im.astype("uint8")
        im = np.vstack((cv.resize(im[:1, :], (angs_options*40, 10)), im))
        plt.imshow(im)
        plt.title("time: " + str(cur_time) + " rockets: " + str(len(rockets_list)))
        plt.pause(0.0001)
    return game_map

import copy
class GameMap:
    def __init__(self):
        self.max_time = 400
        self.max_range = 10000
        self.angs_options = 31
        self.game_map = np.zeros((self.max_time+1, self.angs_options, 3))
        self.game_dict = {(t,a):{} for t in range(self.max_time) for a in range(self.angs_options)}
        self.color_dict = {'empty':[0,0,0]}
        self.old_game_map = np.zeros((self.max_time+1, self.angs_options, 3))
        self.old_game_dict = {(t,a):{} for t in range(self.max_time) for a in range(self.angs_options)}

    def revert(self):
        self.game_map = self.old_game_map.copy()
        self.game_dict = copy.deepcopy(self.old_game_dict)

    def update_old(self):
        self.old_game_map = self.game_map.copy()
        self.old_game_dict = copy.deepcopy(self.game_dict)


    def get_rocket_by_id(self, rockets_list, id):
        for r in rockets_list:
            if r.id == id:
                return r

    def get_color(self, id, city_hit):
        if city_hit:
            COLOR = CITY_COLORS[id % len(CITY_COLORS)]
        else:
            COLOR = FIELD_COLORS[id % len(FIELD_COLORS)]
        return COLOR

    def update_map(self, cur_time, rockets_list, new_rockets, removed_rockets, cur_ang):
        self.update_old()
        self.game_map[:-1] = self.game_map[1:]
        self.game_map[-1] = self.color_dict['empty']

        for a in range(self.angs_options):
            self.game_dict[((cur_time-1)%self.max_time,a)] = {}

        for id in new_rockets:
            r = self.get_rocket_by_id(rockets_list, id)
            self.color_dict[id] = self.get_color(id, r.city_hit)
            for p in r.interception_points:
                if (p[0] < cur_time):
                    continue
                if (p[0] >= cur_time + self.max_time):
                    continue
                dict_key = (p[0] % self.max_time, ang2coord(p[1]))
                self.game_dict[dict_key][id] = p[2]
                cur_dict = self.game_dict[dict_key]
                min_id = min(cur_dict, key=lambda k: cur_dict[k])
                #game map: line 0 - the actor, line 1 - rocket to hit if I shoot now.
                self.game_map[p[0] - cur_time +1, ang2coord(p[1])] = self.color_dict[min_id]

        self.game_map[0, :, :] = 0
        print("actor location: " + str(ang2coord(cur_ang)))
        self.game_map[0, ang2coord(cur_ang), :] = GREEN
        return self.game_map

    def delete_rockets_path_after_shoot(self):
        return




def main():
    a = 1


if __name__ == '__main__':
    main()
