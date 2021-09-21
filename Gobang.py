from graphics import *

GRID_WIDTH = 40

COLUMN = 6
ROW = 6

list1 = []  # AI
list2 = []  # human
list3 = []  # all

list_all = []  # all points on the board
next_point = [0, 0]  # AI 下一步最应该下的位置

ratio = 1  # aggressive ratio
DEPTH = 3  # search depth, must be odd number, if less than zero, it evaluate player's max score


# evaluate score for different types
shape_score = [(50, (0, 1, 1, 0, 0)),
               (50, (0, 0, 1, 1, 0)),
               (200, (1, 1, 0, 1, 0)),
               (500, (0, 0, 1, 1, 1)),
               (500, (1, 1, 1, 0, 0)),
               (5000, (0, 1, 1, 1, 0)),
               (5000, (0, 1, 0, 1, 1, 0)),
               (5000, (0, 1, 1, 0, 1, 0)),
               (5000, (1, 1, 1, 0, 1)),
               (5000, (1, 1, 0, 1, 1)),
               (5000, (1, 0, 1, 1, 1)),
               (5000, (1, 1, 1, 1, 0)),
               (5000, (0, 1, 1, 1, 1)),
               (50000, (0, 1, 1, 1, 1, 0)),
               (99999999, (1, 1, 1, 1, 1))]


def ai():
    global cut_count  # pruning times
    cut_count = 0
    global search_count  # search times
    search_count = 0
    negative_max(True, DEPTH, -99999999, 99999999)
    print("本次共剪枝次数：" + str(cut_count))
    print("本次共搜索次数：" + str(search_count))
    return next_point[0], next_point[1]


# 负值极大搜索+alpha-beta剪枝算法
def negative_max(is_ai, depth, alpha, beta):
    # if game ends || if search reaches the end of the tree
    if game_win(list1) or game_win(list2) or depth == 0:
        return evaluation(is_ai)

    blank_list = list(set(list_all).difference(set(list3)))
    order(blank_list)  # sort, improve efficiency
    for nextstep in blank_list:
        global search_count
        search_count += 1

        if not has_neighbour(nextstep):
            continue

        if is_ai:
            list1.append(nextstep)
        else:
            list2.append(nextstep)
        list3.append(nextstep)

        value = -negative_max(not is_ai, depth - 1, -beta, -alpha)
        if is_ai:
            list1.remove(nextstep)
        else:
            list2.remove(nextstep)
        list3.remove(nextstep)

        if value > alpha:
            print(str(value) + "alpha: " + str(alpha) + " beta: " + str(beta))
            print(list3)
            if depth == DEPTH:
                next_point[0] = nextstep[0]
                next_point[1] = nextstep[1]
            # alpha-beta pruning point
            if value >= beta:
                global cut_count
                cut_count += 1
                return beta
            alpha = value
    return alpha


# 最后落子的邻居位置可能是最优解
def order(blank_list):
    last_pt = list3[-1]
    for item in blank_list:
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if (last_pt[0] + i, last_pt[1] + j) in blank_list:
                    blank_list.remove((last_pt[0] + i, last_pt[1] + j))
                    blank_list.insert(0, (last_pt[0] + i, last_pt[1] + j))


def has_neighbour(pt):
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            if (pt[0] + i, pt[1] + j) in list3:
                return True
    return False


# 判定有点问题，AI连成4个的时候不一定会直接下在第5个位置
def evaluation(is_ai):
    total_score = 0
    if is_ai:
        my_list = list1
        enemy_list = list2
    else:
        my_list = list2
        enemy_list = list1
    # calculate my score
    score_all_arr = []  # position of score shape, if cross, multiples
    my_score = 0
    for pt in my_list:
        m = pt[0]
        n = pt[1]
        my_score += cal_score(m, n, 0, 1, enemy_list, my_list, score_all_arr)  # 横向
        my_score += cal_score(m, n, 1, 0, enemy_list, my_list, score_all_arr)  # 纵向
        my_score += cal_score(m, n, 1, 1, enemy_list, my_list, score_all_arr)  # 对角线
        my_score += cal_score(m, n, -1, 1, enemy_list, my_list, score_all_arr)  # ？

    score_all_arr_enemy = []
    enemy_score = 0
    for pt in enemy_list:
        m = pt[0]
        n = pt[1]
        enemy_score += cal_score(m, n, 0, 1, my_list, enemy_list, score_all_arr_enemy)
        enemy_score += cal_score(m, n, 1, 0, my_list, enemy_list, score_all_arr_enemy)
        enemy_score += cal_score(m, n, 1, 1, my_list, enemy_list, score_all_arr_enemy)
        enemy_score += cal_score(m, n, -1, 1, my_list, enemy_list, score_all_arr_enemy)

    total_score = my_score - enemy_score * ratio * 0.1
    return total_score


def cal_score(m, n, x_decrict, y_derice, enemy_list, my_list, score_all_arr):
    add_score = 0  # 加分项
    # 在一个方向上， 只取最大的得分项
    max_score_shape = (0, None)

    # 如果此方向上，该点已经有得分形状，不重复计算
    for item in score_all_arr:
        for pt in item[1]:
            if m == pt[0] and n == pt[1] and x_decrict == item[2][0] and y_derice == item[2][1]:
                return 0

    # 在落子点 左右方向上循环查找得分形状
    for offset in range(-5, 1):
        # offset = -2
        pos = []
        for i in range(0, 6):
            if (m + (i + offset) * x_decrict, n + (i + offset) * y_derice) in enemy_list:
                pos.append(2)
            elif (m + (i + offset) * x_decrict, n + (i + offset) * y_derice) in my_list:
                pos.append(1)
            else:
                pos.append(0)
        tmp_shap5 = (pos[0], pos[1], pos[2], pos[3], pos[4])
        tmp_shap6 = (pos[0], pos[1], pos[2], pos[3], pos[4], pos[5])

        for (score, shape) in shape_score:
            if tmp_shap5 == shape or tmp_shap6 == shape:
                if tmp_shap5 == (1,1,1,1,1):
                    print('wwwwwwwwwwwwwwwwwwwwwwwwwww')
                if score > max_score_shape[0]:
                    max_score_shape = (score, ((m + (0+offset) * x_decrict, n + (0+offset) * y_derice),
                                               (m + (1+offset) * x_decrict, n + (1+offset) * y_derice),
                                               (m + (2+offset) * x_decrict, n + (2+offset) * y_derice),
                                               (m + (3+offset) * x_decrict, n + (3+offset) * y_derice),
                                               (m + (4+offset) * x_decrict, n + (4+offset) * y_derice)), (x_decrict, y_derice))

    # 计算两个形状相交， 如两个3活 相交， 得分增加 一个子的除外
    if max_score_shape[1] is not None:
        for item in score_all_arr:
            for pt1 in item[1]:
                for pt2 in max_score_shape[1]:
                    if pt1 == pt2 and max_score_shape[0] > 10 and item[0] > 10:
                        add_score += item[0] + max_score_shape[0]

        score_all_arr.append(max_score_shape)

    return add_score + max_score_shape[0]


# judge if one of the players wins
def game_win(list):
    for m in range(COLUMN):
        for n in range(ROW):
            if n < ROW - 4 and (m, n) in list and (m, n + 1) in list and (m, n + 2) in list and (
                    m, n + 3) in list and (m, n + 4) in list:
                return True
            elif m < ROW - 4 and (m, n) in list and (m + 1, n) in list and (m + 2, n) in list and (
                    m + 3, n) in list and (m + 4, n) in list:
                return True
            elif m < ROW - 4 and n < ROW - 4 and (m, n) in list and (m + 1, n + 1) in list and (
                    m + 2, n + 2) in list and (m + 3, n + 3) in list and (m + 4, n + 4) in list:
                return True
            elif m < ROW - 4 and n > 3 and (m, n) in list and (m + 1, n - 1) in list and (
                    m + 2, n - 2) in list and (m + 3, n - 3) in list and (m + 4, n - 4) in list:
                return True
    return False


def gobangwin():
    win = GraphWin("Gobang with Kris Wang", GRID_WIDTH * COLUMN, GRID_WIDTH * ROW)
    win.setBackground("yellow")
    i1 = 0
    while i1 <= GRID_WIDTH * COLUMN:
        l = Line(Point(i1, 0), Point(i1, GRID_WIDTH * ROW))
        l.draw(win)
        i1 += GRID_WIDTH
    i2 = 0
    while i2 <= GRID_WIDTH * ROW:
        l = Line(Point(0, i2), Point(GRID_WIDTH * COLUMN, i2))
        l.draw(win)
        i2 += GRID_WIDTH
    return win


# calculate the score from each side
# def cal_score(m, n, x_direction, y_direction, enemy_list, my_list, score_all_arr):
#     # score_all_arr is like:
#     # [x-axis, y-axis, [score on x direction, score on y direction]]
#     add_score = 0  # 每个加分项
#     # 在每个方向上只取最大的加分项
#     max_score_shape = (0, None)
#
#     # 如果在该方向上已经存在得分形状，不重复计算
#     for item in score_all_arr:
#         for pt in item[1]:
#             if m == pt[0] and n == pt[1] and x_direction == item[2][0] and y_direction == item[2][1]:
#                 return 0
#
#     # 在落子点，左右方向上循环查找得分形状
#     for offset in range(-5, 1):
#         pos = []
#         for i in range(0, 6):
#             if (m + (i + offset) * x_direction, n + (i + offset) * y_direction) in enemy_list:
#                 pos.append(2)
#             elif (m + (i + offset) * x_direction, n + (i + offset) * y_direction) in my_list:
#                 pos.append(1)
#             else:
#                 pos.append(0)
#         tmp_shap5 = (pos[0], pos[1], pos[2], pos[3], pos[4])
#         tmp_shap6 = (pos[0], pos[1], pos[2], pos[3], pos[4], pos[5])
#
#         for (score, shape) in shape_score:
#             if tmp_shap5 == shape or tmp_shap6 == shape:
#                 if tmp_shap5 == (1, 1, 1, 1, 1):
#                     print('wwwwwwwwwwwwwwwwwwwwwwwwwww')
#                 if score > max_score_shape[0]:
#                     max_score_shape = (score, ((m + (0 + offset) * x_direction, n + (0 + offset) * y_direction),
#                                                (m + (1 + offset) * x_direction, n + (1 + offset) * y_direction),
#                                                (m + (2 + offset) * x_direction, n + (2 + offset) * y_direction),
#                                                (m + (3 + offset) * x_direction, n + (3 + offset) * y_direction),
#                                                (m + (4 + offset) * x_direction, n + (4 + offset) * y_direction)),
#                                        (x_direction, y_direction))
#     # 计算两个形状相交， e.g. 3-line cross, except 1-line cross
#     if max_score_shape[1] is not None:
#         for item in score_all_arr:
#             for pt1 in item[1]:
#                 for pt2 in max_score_shape[1]:
#                     if pt1 == pt2 and max_score_shape[0] > 10 and item[0] > 10:
#                         add_score += item[0] + max_score_shape[0]
#
#         score_all_arr.append(max_score_shape)
#
#     return add_score + max_score_shape[0]


if __name__ == '__main__':
    win = gobangwin()

    for i in range(COLUMN + 1):
        for j in range(ROW + 1):
            list_all.append((i, j))

    change = 0
    g = 0
    m = 0
    n = 0

    while g == 0:
        if change % 2 == 1:
            # ai playing
            pos = ai()
            if pos in list3:
                message = Text(Point(200, 200), "不可用的位置" + str(pos[0]) + ", " + str(pos[1]))
                message.draw(win)
                g = 1
            list1.append(pos)
            list3.append(pos)
            piece = Circle(Point(GRID_WIDTH * pos[0], GRID_WIDTH * pos[1]), 16)
            piece.setFill('white')
            piece.draw(win)
            if game_win(list1):
                message = Text(Point(100, 100), "white win.")
                message.draw(win)
                g = 1
            change += 1
        else:
            # human playing
            p2 = win.getMouse()
            if not ((round((p2.getX()) / GRID_WIDTH), round((p2.getY()) / GRID_WIDTH)) in list3):
                a2 = round((p2.getX()) / GRID_WIDTH)
                b2 = round((p2.getY()) / GRID_WIDTH)
                list2.append((a2, b2))
                list3.append((a2, b2))

                piece = Circle(Point(GRID_WIDTH * a2, GRID_WIDTH * b2), 16)
                piece.setFill('black')
                piece.draw(win)
                if game_win(list2):
                    message = Text(Point(100, 100), "black win.")
                    message.draw(win)
                    g = 1
                change += 1

    message = Text(Point(100, 120), "Click anywhere to quit.")
    message.draw(win)
    win.getMouse()
    win.close()

