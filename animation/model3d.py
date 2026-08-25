import math
from OpenGL.GL import *
from OpenGL.GLU import *


def draw_sphere(radius, slices=20, stacks=14):
    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)
    gluSphere(quad, radius, slices, stacks)
    gluDeleteQuadric(quad)


def draw_cylinder(radius, height, slices=16):
    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    gluCylinder(quad, radius, radius, height, slices, 1)
    glPopMatrix()
    gluDeleteQuadric(quad)


def draw_tapered_cylinder(base_r, top_r, height, slices=16):
    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    gluCylinder(quad, base_r, top_r, height, slices, 1)
    glPopMatrix()
    gluDeleteQuadric(quad)


SKIN = (0.92, 0.75, 0.55)
SHIRT = (0.2, 0.5, 0.8)
PANTS = (0.25, 0.25, 0.45)
SHOE = (0.2, 0.15, 0.1)
DARK = (0.12, 0.12, 0.12)


class HumanoidModel:
    def __init__(self):
        self.left_shoulder_angle = 15
        self.left_elbow_angle = -10
        self.left_wrist_angle = 0
        self.right_shoulder_angle = -15
        self.right_elbow_angle = -10
        self.right_wrist_angle = 0
        self.finger_spread = 0.3
        self.thumb_out = 0.5
        self.index_up = 0.3
        self.middle_up = 0.3
        self.ring_up = 0.3
        self.pinky_up = 0.3
        self.index_hook = 0.0

    def set_pose(self, pose_name: str):
        poses = POSE_3D_MAP.get(pose_name, POSE_3D_MAP["idle"])
        for key, val in poses.items():
            if hasattr(self, key):
                setattr(self, key, val)

    def draw(self):
        self._draw_torso()
        self._draw_head()
        self._draw_left_arm()
        self._draw_right_arm()
        self._draw_left_leg()
        self._draw_right_leg()

    def _draw_torso(self):
        glColor3f(*SHIRT)
        glPushMatrix()
        glTranslatef(0, 1.7, 0)
        draw_tapered_cylinder(0.32, 0.38, 1.3)
        glPopMatrix()

        glColor3f(*SHIRT)
        glPushMatrix()
        glTranslatef(0, 2.35, 0)
        draw_sphere(0.4)
        glPopMatrix()

    def _draw_head(self):
        glPushMatrix()
        glTranslatef(0, 3.1, 0)
        glColor3f(*SKIN)
        draw_sphere(0.35, 22, 16)

        glColor3f(*DARK)
        glPushMatrix()
        glTranslatef(-0.1, 0.06, 0.3)
        draw_sphere(0.04)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0.1, 0.06, 0.3)
        draw_sphere(0.04)
        glPopMatrix()

        glColor3f(0.75, 0.4, 0.4)
        glPushMatrix()
        glTranslatef(0, -0.06, 0.35)
        draw_sphere(0.05)
        glPopMatrix()

        glColor3f(*SKIN)
        glPushMatrix()
        glTranslatef(-0.22, 0.3, 0)
        glRotatef(-10, 0, 0, 1)
        draw_cylinder(0.05, 0.2)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0.22, 0.3, 0)
        glRotatef(10, 0, 0, 1)
        draw_cylinder(0.05, 0.2)
        glPopMatrix()

        glColor3f(0.15, 0.1, 0.08)
        glPushMatrix()
        glTranslatef(0, 0.35, 0)
        draw_tapered_cylinder(0.33, 0.28, 0.2)
        glPopMatrix()

        glPopMatrix()

    def _draw_arm(self, side=1):
        shoulder_x = side * 0.52
        shoulder_y = 2.55
        shoulder_angle = self.left_shoulder_angle if side < 0 else self.right_shoulder_angle
        elbow_angle = self.left_elbow_angle if side < 0 else self.right_elbow_angle
        wrist_angle = self.left_wrist_angle if side < 0 else self.right_wrist_angle

        glPushMatrix()
        glTranslatef(shoulder_x, shoulder_y, 0)
        glRotatef(side * shoulder_angle, 0, 0, 1)

        glColor3f(*SHIRT)
        draw_cylinder(0.09, 0.45)

        glTranslatef(0, -0.32, 0)
        glColor3f(*SKIN)
        draw_cylinder(0.08, 0.4)

        glTranslatef(0, -0.28, 0)
        glRotatef(elbow_angle, 1, 0, 0)
        glColor3f(*SKIN)
        draw_cylinder(0.07, 0.35)

        glTranslatef(0, -0.25, 0)
        glRotatef(wrist_angle, 1, 0, 0)
        self._draw_hand(side)

        glPopMatrix()

    def _draw_left_arm(self):
        self._draw_arm(-1)

    def _draw_right_arm(self):
        self._draw_arm(1)

    def _draw_hand(self, side=1):
        glColor3f(*SKIN)
        draw_sphere(0.065)

        finger_len = 0.1
        thumb_len = 0.08
        spread = 0.03 + self.finger_spread * 0.02

        base_x = [-spread * 1.5, -spread * 0.5, spread * 0.5, spread * 1.5]
        base_up = [self.index_up, self.middle_up, self.ring_up, self.pinky_up]
        hook = [self.index_hook, 0, 0, 0]

        for i in range(4):
            glPushMatrix()
            glTranslatef(base_x[i], -0.06, 0)
            glRotatef(hook[i] * 40, 1, 0, 0)
            glColor3f(*SKIN)
            draw_cylinder(0.02, finger_len)

            tip_up = base_up[i] * 0.05
            glTranslatef(0, -finger_len * 0.5, tip_up)
            draw_cylinder(0.015, finger_len * 0.55)
            glPopMatrix()

        glPushMatrix()
        thumb_x = side * 0.08
        glTranslatef(thumb_x, -0.01, self.thumb_out * 0.06)
        glRotatef(-25 * side, 0, 0, 1)
        glColor3f(*SKIN)
        draw_cylinder(0.022, thumb_len)
        glTranslatef(0, -thumb_len * 0.5, 0)
        draw_cylinder(0.017, thumb_len * 0.5)
        glPopMatrix()

    def _draw_leg(self, side=1):
        leg_x = side * 0.18
        hip_y = 1.3

        glPushMatrix()
        glTranslatef(leg_x, hip_y, 0)
        glColor3f(*PANTS)
        draw_cylinder(0.12, 0.8)

        glTranslatef(0, -0.5, 0)
        draw_cylinder(0.1, 0.7)

        glTranslatef(0, -0.45, 0.05)
        glColor3f(*SHOE)
        draw_tapered_cylinder(0.1, 0.08, 0.25)
        glTranslatef(0, -0.05, 0.08)
        draw_sphere(0.1)
        glPopMatrix()

    def _draw_left_leg(self):
        self._draw_leg(-1)

    def _draw_right_leg(self):
        self._draw_leg(1)


POSE_3D_MAP = {
    "idle": {
        "left_shoulder_angle": 15,
        "left_elbow_angle": -10,
        "right_shoulder_angle": -15,
        "right_elbow_angle": -10,
        "finger_spread": 0.3,
        "thumb_out": 0.5,
        "index_up": 0.3,
        "middle_up": 0.3,
        "ring_up": 0.3,
        "pinky_up": 0.3,
        "index_hook": 0,
    },
    "fist_thumb_side": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "right_wrist_angle": 0,
        "finger_spread": 0,
        "thumb_out": 1.0,
        "index_up": 0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "flat_palm": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.2,
        "thumb_out": 0.3,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 1.0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "c_curve": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "right_wrist_angle": -20,
        "finger_spread": 0.3,
        "thumb_out": 0.5,
        "index_up": 0.7,
        "middle_up": 0.7,
        "ring_up": 0.7,
        "pinky_up": 0.7,
        "index_hook": 0.3,
    },
    "index_up_circle": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0,
        "thumb_out": 0.8,
        "index_up": 1.0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "claw_closed": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.1,
        "thumb_out": 0.2,
        "index_up": 0.3,
        "middle_up": 0.3,
        "ring_up": 0.3,
        "pinky_up": 0.3,
        "index_hook": 0.6,
    },
    "ok_outside": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.5,
        "thumb_out": 0.9,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 1.0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "pinch_up": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.1,
        "thumb_out": 0.9,
        "index_up": 1.0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "two_fingers_horizontal": {
        "right_shoulder_angle": -30,
        "right_elbow_angle": -90,
        "right_wrist_angle": -90,
        "finger_spread": 0.3,
        "thumb_out": 0.5,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "pinky_up": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0,
        "thumb_out": 0.2,
        "index_up": 0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "pinky_hook": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0,
        "thumb_out": 0.2,
        "index_up": 0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0.7,
        "index_hook": 0,
    },
    "two_fingers_up": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.1,
        "thumb_out": 0.3,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "l_shape": {
        "right_shoulder_angle": -45,
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
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.2,
        "thumb_out": 0.1,
        "index_up": 0.1,
        "middle_up": 0.1,
        "ring_up": 0.1,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "two_over_thumb": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.1,
        "thumb_out": 0.1,
        "index_up": 0.1,
        "middle_up": 0.1,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "circle": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "right_wrist_angle": -10,
        "finger_spread": 0.2,
        "thumb_out": 0.7,
        "index_up": 0.5,
        "middle_up": 0.5,
        "ring_up": 0.5,
        "pinky_up": 0.5,
        "index_hook": 0.3,
    },
    "two_fingers_down": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "right_wrist_angle": 40,
        "finger_spread": 0.1,
        "thumb_out": 0.3,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "pinch_down": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "right_wrist_angle": 30,
        "finger_spread": 0.1,
        "thumb_out": 0.9,
        "index_up": 1.0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "crossed_fingers": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0,
        "thumb_out": 0.2,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "fist_thumb_front": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0,
        "thumb_out": 0.5,
        "index_up": 0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "thumb_inside": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.1,
        "thumb_out": 0.0,
        "index_up": 0.1,
        "middle_up": 0.1,
        "ring_up": 0.1,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "two_fingers_together": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0,
        "thumb_out": 0.2,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "v_shape": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.5,
        "thumb_out": 0.3,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "three_fingers_spread": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.6,
        "thumb_out": 0.2,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 1.0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "hook_index": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0,
        "thumb_out": 0.3,
        "index_up": 0.3,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0.8,
    },
    "shaka": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.5,
        "thumb_out": 1.0,
        "index_up": 0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "index_trace": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0,
        "thumb_out": 0.3,
        "index_up": 1.0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0.2,
    },
    "zero_sphere": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.2,
        "thumb_out": 0.7,
        "index_up": 0.5,
        "middle_up": 0.5,
        "ring_up": 0.5,
        "pinky_up": 0.5,
        "index_hook": 0.3,
    },
    "one_index": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0,
        "thumb_out": 0.2,
        "index_up": 1.0,
        "middle_up": 0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "two_v": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.5,
        "thumb_out": 0.3,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "three_thumb_v": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.4,
        "thumb_out": 1.0,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0,
        "pinky_up": 0,
        "index_hook": 0,
    },
    "four_fingers": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.3,
        "thumb_out": 0.1,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 1.0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "five_open": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.6,
        "thumb_out": 1.0,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 1.0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "six_thumb_index": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.3,
        "thumb_out": 0.5,
        "index_up": 0.6,
        "middle_up": 1.0,
        "ring_up": 1.0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "seven_thumb_ring": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.3,
        "thumb_out": 0.5,
        "index_up": 1.0,
        "middle_up": 1.0,
        "ring_up": 0.6,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "eight_thumb_middle": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.3,
        "thumb_out": 0.5,
        "index_up": 1.0,
        "middle_up": 0.6,
        "ring_up": 1.0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
    "nine_thumb_index_in": {
        "right_shoulder_angle": -45,
        "right_elbow_angle": -60,
        "finger_spread": 0.3,
        "thumb_out": 0.5,
        "index_up": 0.6,
        "middle_up": 1.0,
        "ring_up": 1.0,
        "pinky_up": 1.0,
        "index_hook": 0,
    },
}
