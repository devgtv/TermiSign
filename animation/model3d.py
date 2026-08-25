import math
from OpenGL.GL import *
from OpenGL.GLU import *


def _sphere(radius, slices=16, stacks=10):
    q = gluNewQuadric()
    gluQuadricNormals(q, GLU_SMOOTH)
    gluSphere(q, radius, slices, stacks)
    gluDeleteQuadric(q)


def _cylinder(radius, height, slices=8):
    q = gluNewQuadric()
    gluQuadricNormals(q, GLU_SMOOTH)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    gluCylinder(q, radius, radius, height, slices, 1)
    glPopMatrix()
    gluDeleteQuadric(q)


def _limb(x1, y1, z1, x2, y2, z2, radius, color):
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1
    length = math.sqrt(dx*dx + dy*dy + dz*dz)
    if length < 0.001:
        return

    glPushMatrix()
    glTranslatef(x1, y1, z1)
    glColor3f(*color)

    yaw = math.degrees(math.atan2(dx, dz))
    pitch = math.degrees(math.atan2(-dy, math.sqrt(dx*dx + dz*dz)))

    glRotatef(yaw, 0, 1, 0)
    glRotatef(pitch, 1, 0, 0)
    _cylinder(radius, length)
    glPopMatrix()


STICK = (0.85, 0.85, 0.9)
HAND_COLOR = (1.0, 0.75, 0.5)
JOINT_COLOR = (0.95, 0.85, 0.65)
HEAD_COLOR = (0.95, 0.85, 0.65)
EYE_COLOR = (0.1, 0.1, 0.1)


class HumanoidModel:
    def __init__(self):
        self.left_shoulder_angle = 10
        self.left_elbow_angle = 0
        self.left_wrist_angle = 0
        self.right_shoulder_angle = -10
        self.right_elbow_angle = 0
        self.right_wrist_angle = 0
        self.finger_spread = 0.2
        self.thumb_out = 0.4
        self.index_up = 0.5
        self.middle_up = 0.5
        self.ring_up = 0.5
        self.pinky_up = 0.5
        self.index_hook = 0.0

    def set_pose(self, pose_name: str):
        for k, v in POSE_3D_MAP.get(pose_name, POSE_3D_MAP["idle"]).items():
            if hasattr(self, k):
                setattr(self, k, v)

    def draw(self):
        head_y = 4.2
        neck_y = 3.85
        shoulder_y = 3.7
        torso_bot = 2.4
        hip_y = 2.3
        knee_y = 1.2
        foot_y = 0.0

        shoulder_x = 0.55
        hip_x = 0.2

        _limb(0, torso_bot, 0, 0, neck_y, 0, 0.04, STICK)

        _limb(-hip_x, hip_y, 0, -hip_x, knee_y, 0, 0.035, STICK)
        _limb(-hip_x, knee_y, 0, -hip_x * 0.9, foot_y, 0.1, 0.035, STICK)

        _limb(hip_x, hip_y, 0, hip_x, knee_y, 0, 0.035, STICK)
        _limb(hip_x, knee_y, 0, hip_x * 0.9, foot_y, 0.1, 0.035, STICK)

        _limb(-hip_x * 0.9, foot_y, 0.1, -hip_x * 0.9, foot_y, 0.3, 0.03, STICK)
        _limb(hip_x * 0.9, foot_y, 0.1, hip_x * 0.9, foot_y, 0.3, 0.03, STICK)

        self._draw_arm(-1, -shoulder_x, shoulder_y, torso_bot)
        self._draw_arm(1, shoulder_x, shoulder_y, torso_bot)

        glPushMatrix()
        glTranslatef(0, head_y, 0)
        glColor3f(*HEAD_COLOR)
        _sphere(0.3, 18, 14)

        glPushMatrix()
        glTranslatef(-0.1, 0.05, 0.26)
        glColor3f(*EYE_COLOR)
        _sphere(0.04)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0.1, 0.05, 0.26)
        glColor3f(*EYE_COLOR)
        _sphere(0.04)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0, -0.08, 0.3)
        glColor3f(0.8, 0.3, 0.3)
        _sphere(0.035)
        glPopMatrix()
        glPopMatrix()

    def _draw_arm(self, side, sx, sy, torso_bot):
        shoulder_angle = self.left_shoulder_angle if side < 0 else self.right_shoulder_angle
        elbow_angle = self.left_elbow_angle if side < 0 else self.right_elbow_angle
        wrist_angle = self.left_wrist_angle if side < 0 else self.right_wrist_angle

        rad = math.radians(shoulder_angle * side)
        upper_len = 0.9
        elbow_x = sx + math.sin(rad) * upper_len
        elbow_y = sy - math.cos(rad) * upper_len

        _limb(sx, sy, 0, elbow_x, elbow_y, 0, 0.035, STICK)

        glPushMatrix()
        glTranslatef(elbow_x, elbow_y, 0)
        glRotatef(side * shoulder_angle, 0, 0, 1)
        glRotatef(elbow_angle, 0, 0, 1)

        lower_len = 0.75
        wx = math.sin(math.radians(elbow_angle)) * lower_len
        wy = -math.cos(math.radians(elbow_angle)) * lower_len

        _limb(0, 0, 0, wx, wy, 0, 0.03, STICK)

        glTranslatef(wx, wy, 0)
        glRotatef(wrist_angle, 0, 0, 1)
        self._draw_hand(side)
        glPopMatrix()

    def _draw_hand(self, side):
        palm_r = 0.12
        glPushMatrix()
        glColor3f(*HAND_COLOR)
        _sphere(palm_r, 14, 10)

        finger_len = 0.22
        thumb_len = 0.16
        spread = 0.06 + self.finger_spread * 0.04

        finger_data = [
            (-spread * 1.8, self.index_up, self.index_hook),
            (-spread * 0.6, self.middle_up, 0),
            (spread * 0.6, self.ring_up, 0),
            (spread * 1.8, self.pinky_up, 0),
        ]

        for fx, up_amount, hook_amount in finger_data:
            tip_x = fx + math.sin(math.radians(hook_amount * 50)) * finger_len * 0.3
            tip_y = -finger_len + up_amount * finger_len * 0.4
            tip_z = hook_amount * finger_len * 0.2

            _limb(fx * 0.5, -palm_r * 0.5, 0, tip_x, tip_y, tip_z, 0.025, HAND_COLOR)
            _sphere_at(tip_x, tip_y, tip_z, 0.03, HAND_COLOR)

        thumb_x = side * 0.16
        thumb_base_y = -0.02
        thumb_tip_x = thumb_x + side * self.thumb_out * 0.15
        thumb_tip_y = thumb_base_y + 0.05
        thumb_tip_z = 0.05

        _limb(thumb_x * 0.5, thumb_base_y, 0, thumb_tip_x, thumb_tip_y, thumb_tip_z, 0.03, HAND_COLOR)
        _sphere_at(thumb_tip_x, thumb_tip_y, thumb_tip_z, 0.035, HAND_COLOR)

        glPopMatrix()


def _sphere_at(x, y, z, radius, color):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(*color)
    _sphere(radius, 10, 8)
    glPopMatrix()


POSE_3D_MAP = {
    "idle": {
        "left_shoulder_angle": 10,
        "left_elbow_angle": 0,
        "right_shoulder_angle": -10,
        "right_elbow_angle": 0,
        "finger_spread": 0.2,
        "thumb_out": 0.4,
        "index_up": 0.5,
        "middle_up": 0.5,
        "ring_up": 0.5,
        "pinky_up": 0.5,
        "index_hook": 0,
    },
    "fist_thumb_side": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0,
        "thumb_out": 1.0,
        "index_up": 0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "flat_palm": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.3,
        "thumb_out": 0.3,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 1.0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "c_curve": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.2,
        "thumb_out": 0.5,
        "index_up": 0.7,
        "middle_up": 0.7,
        "ring_up": 0.7,
        "pinky_up": 0.7,
        "index_hook": 0.3,
    },
    "index_up_circle": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0,
        "thumb_out": 0.8,
        "index_up": 1.0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "claw_closed": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.1,
        "thumb_out": 0.2,
        "index_up": 0.3,
        "middle_up": 0.3,
        "ring_up": 0.3,
        "pinky_up": 0.3,
        "index_hook": 0.6,
    },
    "ok_outside": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.5,
        "thumb_out": 0.9,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 1.0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "pinch_up": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.1,
        "thumb_out": 0.9,
        "index_up": 1.0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "two_fingers_horizontal": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -90,
        "finger_spread": 0.3,
        "thumb_out": 0.5,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "pinky_up": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0,
        "thumb_out": 0.2,
        "index_up": 0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "pinky_hook": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0,
        "thumb_out": 0.2,
        "index_up": 0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0.7,
        "index_hook": 0,
    },
    "two_fingers_up": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.15,
        "thumb_out": 0.3,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "l_shape": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -90,
        "finger_spread": 0,
        "thumb_out": 1.0,
        "index_up": 1.0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "three_over_thumb": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.2,
        "thumb_out": 0.1,
        "index_up": 0.1,
        "middle_up": 0.1,
        "ring_up": 0.1,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "two_over_thumb": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.1,
        "thumb_out": 0.1,
        "index_up": 0.1,
        "middle_up": 0.1,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "circle": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.2,
        "thumb_out": 0.7,
        "index_up": 0.5,
        "middle_up": 0.5,
        "ring_up": 0.5,
        "pinky_up": 0.5,
        "index_hook": 0.3,
    },
    "two_fingers_down": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.15,
        "thumb_out": 0.3,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "pinch_down": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.1,
        "thumb_out": 0.9,
        "index_up": 1.0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "crossed_fingers": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0,
        "thumb_out": 0.2,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "fist_thumb_front": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0,
        "thumb_out": 0.5,
        "index_up": 0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "thumb_inside": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.1,
        "thumb_out": 0.0,
        "index_up": 0.1,
        "middle_up": 0.1,
        "ring_up": 0.1,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "two_fingers_together": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0,
        "thumb_out": 0.2,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "v_shape": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.5,
        "thumb_out": 0.3,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "three_fingers_spread": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.6,
        "thumb_out": 0.2,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 1.0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "hook_index": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0,
        "thumb_out": 0.3,
        "index_up": 0.3,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0.8,
    },
    "shaka": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.5,
        "thumb_out": 1.0,
        "index_up": 0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "index_trace": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0,
        "thumb_out": 0.3,
        "index_up": 1.0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0.2,
    },
    "zero_sphere": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.2,
        "thumb_out": 0.7,
        "index_up": 0.5,
        "middle_up": 0.5,
        "ring_up": 0.5,
        "pinky_up": 0.5,
        "index_hook": 0.3,
    },
    "one_index": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0,
        "thumb_out": 0.2,
        "index_up": 1.0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "two_v": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.5,
        "thumb_out": 0.3,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "three_thumb_v": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.4,
        "thumb_out": 1.0,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "four_fingers": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.3,
        "thumb_out": 0.1,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 1.0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "five_open": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.6,
        "thumb_out": 1.0,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 1.0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "six_thumb_index": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.3,
        "thumb_out": 0.5,
        "index_up": 0.6,
        "middle_up": 1.0,
        "ring_up": 1.0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "seven_thumb_ring": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.3,
        "thumb_out": 0.5,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0.6,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "eight_thumb_middle": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.3,
        "thumb_out": 0.5,
        "index_up": 1.0,
        "middle_up": 0.6,
        "ring_up": 1.0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "nine_thumb_index_in": {
        "right_shoulder_angle": -60,
        "right_elbow_angle": -40,
        "finger_spread": 0.3,
        "thumb_out": 0.5,
        "index_up": 0.6,
        "middle_up": 1.0,
        "ring_up": 1.0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
}
