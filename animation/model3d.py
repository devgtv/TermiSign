import math
import numpy as np
import trimesh
from OpenGL.GL import *


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

        self._body_vbo = None
        self._left_arm_v = None
        self._right_arm_v = None
        self._build_meshes()
        self._left_arm_v, self._left_arm_f = self._build_arm_vbo(-1)
        self._right_arm_v, self._right_arm_f = self._build_arm_vbo(1)

    def _cylinder_mesh(self, radius, height, segments=12):
        theta = np.linspace(0, 2 * np.pi, segments, endpoint=False)
        x = np.cos(theta) * radius
        z = np.sin(theta) * radius
        top = np.column_stack([x, np.full(segments, height / 2), z])
        bot = np.column_stack([x, np.full(segments, -height / 2), z])
        verts = np.vstack([top, bot])
        faces = []
        for i in range(segments):
            j = (i + 1) % segments
            faces.append([i, j, j + segments])
            faces.append([i, j + segments, i + segments])
        cap_top = [list(range(segments))]
        cap_bot = [list(range(segments, 2 * segments))]
        return verts, np.array(faces), cap_top[0], cap_bot[0]

    def _sphere_mesh(self, radius, rings=8, sectors=12):
        verts = []
        faces = []
        for i in range(rings + 1):
            phi = math.pi * i / rings
            for j in range(sectors):
                theta = 2 * math.pi * j / sectors
                x = radius * math.sin(phi) * math.cos(theta)
                y = radius * math.cos(phi)
                z = radius * math.sin(phi) * math.sin(theta)
                verts.append([x, y, z])
        verts = np.array(verts)
        for i in range(rings):
            for j in range(sectors):
                a = i * sectors + j
                b = i * sectors + (j + 1) % sectors
                c = (i + 1) * sectors + (j + 1) % sectors
                d = (i + 1) * sectors + j
                faces.append([a, b, c])
                faces.append([a, c, d])
        return verts, np.array(faces)

    def _build_meshes(self):
        body_v, body_f = [], []

        hv, hf = self._sphere_mesh(0.32, 10, 14)
        hv[:, 1] += 4.2
        body_v.append(hv)
        body_f.append(hf)

        ev, ef = self._sphere_mesh(0.035, 6, 8)
        ev[:, 1] += 4.22
        ev[:, 0] -= 0.1
        ev[:, 2] += 0.28
        body_v.append(ev)
        body_f.append(ef)

        ev2, ef2 = self._sphere_mesh(0.035, 6, 8)
        ev2[:, 1] += 4.22
        ev2[:, 0] += 0.1
        ev2[:, 2] += 0.28
        body_v.append(ev2)
        body_f.append(ef2)

        nv, nf, _, _ = self._cylinder_mesh(0.06, 0.35)
        nv[:, 1] += 4.0
        body_v.append(nv)
        body_f.append(nf)

        tv, tf, _, _ = self._cylinder_mesh(0.04, 1.4)
        tv[:, 1] += 3.0
        body_v.append(tv)
        body_f.append(tf)

        hv2, hf2 = self._sphere_mesh(0.05, 6, 8)
        hv2[:, 1] += 3.7
        hv2[:, 0] -= 0.55
        body_v.append(hv2)
        body_f.append(hf2)

        hv3, hf3 = self._sphere_mesh(0.05, 6, 8)
        hv3[:, 1] += 3.7
        hv3[:, 0] += 0.55
        body_v.append(hv3)
        body_f.append(hf3)

        self._body_verts = np.concatenate(body_v)
        self._body_faces = self._concat_faces(body_f)

        for side in [-1, 1]:
            hv_s, hf_s = self._sphere_mesh(0.05, 6, 8)
            hv_s[:, 1] += 2.3
            hv_s[:, 0] += side * 0.2

            uv, uf, _, _ = self._cylinder_mesh(0.04, 0.9)
            uv[:, 1] += 1.85
            uv[:, 0] += side * 0.2

            kv, kf = self._sphere_mesh(0.045, 6, 8)
            kv[:, 1] += 1.4
            kv[:, 0] += side * 0.2

            lv, lf, _, _ = self._cylinder_mesh(0.035, 1.0)
            lv[:, 1] += 0.9
            lv[:, 0] += side * 0.2

            fv, ff = self._sphere_mesh(0.04, 6, 8)
            fv[:, 1] += 0.4
            fv[:, 0] += side * 0.2

            av_v = np.concatenate([hv_s, uv, kv, lv, fv])
            av_f = self._concat_faces([hf_s, uf, kf, lf, ff])

            if side < 0:
                self._left_leg_v = av_v
                self._left_leg_f = av_f
            else:
                self._right_leg_v = av_v
                self._right_leg_f = av_f

    def _concat_faces(self, face_lists):
        result = []
        offset = 0
        for faces in face_lists:
            result.append(faces + offset)
            offset += len(faces) if len(faces) > 0 else 0
        return np.concatenate(result) if result else np.array([], dtype=np.int32)

    def _build_arm_vbo(self, side):
        shoulder_angle = self.left_shoulder_angle if side < 0 else self.right_shoulder_angle
        elbow_angle = self.left_elbow_angle if side < 0 else self.right_elbow_angle

        shoulder_x = side * 0.55
        shoulder_y = 3.7

        rad = math.radians(shoulder_angle * side)
        upper_len = 0.9
        elbow_x = shoulder_x + math.sin(rad) * upper_len
        elbow_y = shoulder_y - math.cos(rad) * upper_len

        parts_v, parts_f = [], []

        uv, uf, _, _ = self._cylinder_mesh(0.035, upper_len)
        mx = (shoulder_x + elbow_x) / 2
        my = (shoulder_y + elbow_y) / 2
        angle = math.degrees(math.atan2(elbow_x - shoulder_x, elbow_y - shoulder_y))
        for v in uv:
            x, y, z = v
            rad_a = math.radians(-angle)
            nx = x * math.cos(rad_a) - y * math.sin(rad_a)
            ny = x * math.sin(rad_a) + y * math.cos(rad_a)
            v[0] = nx + mx
            v[1] = ny + my
        parts_v.append(uv)
        parts_f.append(uf)

        jv, jf = self._sphere_mesh(0.045, 6, 8)
        jv[:, 0] += elbow_x
        jv[:, 1] += elbow_y
        parts_v.append(jv)
        parts_f.append(jf)

        elbow_rad = math.radians(elbow_angle)
        lower_len = 0.75
        wx = elbow_x + math.sin(elbow_rad) * lower_len
        wy = elbow_y - math.cos(elbow_rad) * lower_len

        lv, lf, _, _ = self._cylinder_mesh(0.03, lower_len)
        lmx = (elbow_x + wx) / 2
        lmy = (elbow_y + wy) / 2
        langle = math.degrees(math.atan2(wx - elbow_x, wy - elbow_y))
        for v in lv:
            x, y, z = v
            rad_a = math.radians(-langle)
            nx = x * math.cos(rad_a) - y * math.sin(rad_a)
            ny = x * math.sin(rad_a) + y * math.cos(rad_a)
            v[0] = nx + lmx
            v[1] = ny + lmy
        parts_v.append(lv)
        parts_f.append(lf)

        palm_r = 0.12
        pv, pf = self._sphere_mesh(palm_r, 8, 10)
        pv[:, 0] += wx
        pv[:, 1] += wy
        parts_v.append(pv)
        parts_f.append(pf)

        finger_len = 0.22
        spread = 0.06 + self.finger_spread * 0.04
        finger_data = [
            (-spread * 1.8, self.index_up, self.index_hook),
            (-spread * 0.6, self.middle_up, 0),
            (spread * 0.6, self.ring_up, 0),
            (spread * 1.8, self.pinky_up, 0),
        ]

        for fx, up_amount, hook_amount in finger_data:
            tip_x = wx + fx * 0.8
            tip_y = wy - finger_len * (1 - up_amount * 0.3)
            tip_z = hook_amount * finger_len * 0.2

            fv, ff, _, _ = self._cylinder_mesh(0.022, finger_len)
            fmx = (wx + tip_x) / 2
            fmy = (wy + tip_y) / 2
            fangle = math.degrees(math.atan2(tip_x - wx, tip_y - wy))
            for v in fv:
                x, y, z = v
                rad_a = math.radians(-fangle)
                nx = x * math.cos(rad_a) - y * math.sin(rad_a)
                ny = x * math.sin(rad_a) + y * math.cos(rad_a)
                v[0] = nx + fmx
                v[1] = ny + fmy
            parts_v.append(fv)
            parts_f.append(ff)

            ball, ball_f = self._sphere_mesh(0.03, 6, 8)
            ball[:, 0] += tip_x
            ball[:, 1] += tip_y
            parts_v.append(ball)
            parts_f.append(ball_f)

        thumb_x_base = wx + side * 0.16
        thumb_y_base = wy
        thumb_x_tip = thumb_x_base + side * self.thumb_out * 0.15
        thumb_y_tip = thumb_y_base + 0.05
        thumb_z_tip = 0.05

        tv, tf, _, _ = self._cylinder_mesh(0.028, 0.16)
        tmx = (thumb_x_base + thumb_x_tip) / 2
        tmy = (thumb_y_base + thumb_y_tip) / 2
        tangle = math.degrees(math.atan2(thumb_x_tip - thumb_x_base, thumb_y_tip - thumb_y_base))
        for v in tv:
            x, y, z = v
            rad_a = math.radians(-tangle)
            nx = x * math.cos(rad_a) - y * math.sin(rad_a)
            ny = x * math.sin(rad_a) + y * math.cos(rad_a)
            v[0] = nx + tmx
            v[1] = ny + tmy
        parts_v.append(tv)
        parts_f.append(tf)

        tb, tbf = self._sphere_mesh(0.035, 6, 8)
        tb[:, 0] += thumb_x_tip
        tb[:, 1] += thumb_y_tip
        parts_v.append(tb)
        parts_f.append(tbf)

        all_v = np.concatenate(parts_v)
        all_f = self._concat_faces(parts_f)
        return all_v, all_f

    def set_pose(self, pose_name: str):
        for k, v in POSE_3D_MAP.get(pose_name, POSE_3D_MAP["idle"]).items():
            if hasattr(self, k):
                setattr(self, k, v)
        self._left_arm_v, self._left_arm_f = self._build_arm_vbo(-1)
        self._right_arm_v, self._right_arm_f = self._build_arm_vbo(1)

    def draw(self):
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        glColor3f(0.95, 0.85, 0.65)
        self._draw_mesh(self._body_verts, self._body_faces)

        glColor3f(0.85, 0.85, 0.9)
        self._draw_mesh(self._left_leg_v, self._left_leg_f)
        self._draw_mesh(self._right_leg_v, self._right_leg_f)

        glColor3f(0.85, 0.85, 0.9)
        self._draw_mesh(self._left_arm_v, self._left_arm_f)

        glColor3f(1.0, 0.78, 0.55)
        self._draw_mesh(self._right_arm_v, self._right_arm_f)

    def _draw_mesh(self, verts, faces):
        glBegin(GL_TRIANGLES)
        for face in faces:
            if len(face) < 3:
                continue
            v0 = verts[face[0]]
            v1 = verts[face[1]]
            v2 = verts[face[2]]

            e1 = v1 - v0
            e2 = v2 - v0
            n = np.cross(e1, e2)
            norm = np.linalg.norm(n)
            if norm > 0:
                n = n / norm
            else:
                n = np.array([0, 1, 0])

            glNormal3f(*n)
            glVertex3f(*v0)
            glVertex3f(*v1)
            glVertex3f(*v2)
        glEnd()


POSE_3D_MAP = {
    "idle": {
        "left_shoulder_angle": 10, "left_elbow_angle": 0,
        "right_shoulder_angle": -10, "right_elbow_angle": 0,
        "finger_spread": 0.2, "thumb_out": 0.4,
        "index_up": 0.5, "middle_up": 0.5,
        "ring_up": 0.5, "pinky_up": 0.5, "index_hook": 0,
    },
    "fist_thumb_side": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0, "thumb_out": 1.0,
        "index_up": 0, "middle_up": 0, "ring_up": 0, "pinky_up": 0, "index_hook": 0,
    },
    "flat_palm": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.3, "thumb_out": 0.3,
        "index_up": 1.0, "middle_up": 1.0, "ring_up": 1.0, "pinky_up": 1.0, "index_hook": 0,
    },
    "c_curve": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.2, "thumb_out": 0.5,
        "index_up": 0.7, "middle_up": 0.7, "ring_up": 0.7, "pinky_up": 0.7, "index_hook": 0.3,
    },
    "index_up_circle": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0, "thumb_out": 0.8,
        "index_up": 1.0, "middle_up": 0, "ring_up": 0, "pinky_up": 0, "index_hook": 0,
    },
    "claw_closed": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.1, "thumb_out": 0.2,
        "index_up": 0.3, "middle_up": 0.3, "ring_up": 0.3, "pinky_up": 0.3, "index_hook": 0.6,
    },
    "ok_outside": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.5, "thumb_out": 0.9,
        "index_up": 1.0, "middle_up": 1.0, "ring_up": 1.0, "pinky_up": 1.0, "index_hook": 0,
    },
    "pinch_up": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.1, "thumb_out": 0.9,
        "index_up": 1.0, "middle_up": 0, "ring_up": 0, "pinky_up": 0, "index_hook": 0,
    },
    "two_fingers_horizontal": {
        "right_shoulder_angle": -60, "right_elbow_angle": -90,
        "finger_spread": 0.3, "thumb_out": 0.5,
        "index_up": 1.0, "middle_up": 1.0, "ring_up": 0, "pinky_up": 0, "index_hook": 0,
    },
    "pinky_up": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0, "thumb_out": 0.2,
        "index_up": 0, "middle_up": 0, "ring_up": 0, "pinky_up": 1.0, "index_hook": 0,
    },
    "pinky_hook": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0, "thumb_out": 0.2,
        "index_up": 0, "middle_up": 0, "ring_up": 0, "pinky_up": 0.7, "index_hook": 0,
    },
    "two_fingers_up": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.15, "thumb_out": 0.3,
        "index_up": 1.0, "middle_up": 1.0, "ring_up": 0, "pinky_up": 0, "index_hook": 0,
    },
    "l_shape": {
        "right_shoulder_angle": -60, "right_elbow_angle": -90,
        "finger_spread": 0, "thumb_out": 1.0,
        "index_up": 1.0, "middle_up": 0, "ring_up": 0, "pinky_up": 0, "index_hook": 0,
    },
    "three_over_thumb": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.2, "thumb_out": 0.1,
        "index_up": 0.1, "middle_up": 0.1, "ring_up": 0.1, "pinky_up": 0, "index_hook": 0,
    },
    "two_over_thumb": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.1, "thumb_out": 0.1,
        "index_up": 0.1, "middle_up": 0.1, "ring_up": 0, "pinky_up": 0, "index_hook": 0,
    },
    "circle": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.2, "thumb_out": 0.7,
        "index_up": 0.5, "middle_up": 0.5, "ring_up": 0.5, "pinky_up": 0.5, "index_hook": 0.3,
    },
    "two_fingers_down": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.15, "thumb_out": 0.3,
        "index_up": 1.0, "middle_up": 1.0, "ring_up": 0, "pinky_up": 0, "index_hook": 0,
    },
    "pinch_down": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.1, "thumb_out": 0.9,
        "index_up": 1.0, "middle_up": 0, "ring_up": 0, "pinky_up": 0, "index_hook": 0,
    },
    "crossed_fingers": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0, "thumb_out": 0.2,
        "index_up": 1.0, "middle_up": 1.0, "ring_up": 0, "pinky_up": 0, "index_hook": 0,
    },
    "fist_thumb_front": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0, "thumb_out": 0.5,
        "index_up": 0, "middle_up": 0, "ring_up": 0, "pinky_up": 0, "index_hook": 0,
    },
    "thumb_inside": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.1, "thumb_out": 0.0,
        "index_up": 0.1, "middle_up": 0.1, "ring_up": 0.1, "pinky_up": 0, "index_hook": 0,
    },
    "two_fingers_together": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0, "thumb_out": 0.2,
        "index_up": 1.0, "middle_up": 1.0, "ring_up": 0, "pinky_up": 0, "index_hook": 0,
    },
    "v_shape": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.5, "thumb_out": 0.3,
        "index_up": 1.0, "middle_up": 1.0, "ring_up": 0, "pinky_up": 0, "index_hook": 0,
    },
    "three_fingers_spread": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.6, "thumb_out": 0.2,
        "index_up": 1.0, "middle_up": 1.0, "ring_up": 1.0, "pinky_up": 0, "index_hook": 0,
    },
    "hook_index": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0, "thumb_out": 0.3,
        "index_up": 0.3, "middle_up": 0, "ring_up": 0, "pinky_up": 0, "index_hook": 0.8,
    },
    "shaka": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.5, "thumb_out": 1.0,
        "index_up": 0, "middle_up": 0, "ring_up": 0, "pinky_up": 1.0, "index_hook": 0,
    },
    "index_trace": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0, "thumb_out": 0.3,
        "index_up": 1.0, "middle_up": 0, "ring_up": 0, "pinky_up": 0, "index_hook": 0.2,
    },
    "zero_sphere": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.2, "thumb_out": 0.7,
        "index_up": 0.5, "middle_up": 0.5, "ring_up": 0.5, "pinky_up": 0.5, "index_hook": 0.3,
    },
    "one_index": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0, "thumb_out": 0.2,
        "index_up": 1.0, "middle_up": 0, "ring_up": 0, "pinky_up": 0, "index_hook": 0,
    },
    "two_v": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.5, "thumb_out": 0.3,
        "index_up": 1.0, "middle_up": 1.0, "ring_up": 0, "pinky_up": 0, "index_hook": 0,
    },
    "three_thumb_v": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.4, "thumb_out": 1.0,
        "index_up": 1.0, "middle_up": 1.0, "ring_up": 0, "pinky_up": 0, "index_hook": 0,
    },
    "four_fingers": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.3, "thumb_out": 0.1,
        "index_up": 1.0, "middle_up": 1.0, "ring_up": 1.0, "pinky_up": 1.0, "index_hook": 0,
    },
    "five_open": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.6, "thumb_out": 1.0,
        "index_up": 1.0, "middle_up": 1.0, "ring_up": 1.0, "pinky_up": 1.0, "index_hook": 0,
    },
    "six_thumb_index": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.3, "thumb_out": 0.5,
        "index_up": 0.6, "middle_up": 1.0, "ring_up": 1.0, "pinky_up": 1.0, "index_hook": 0,
    },
    "seven_thumb_ring": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.3, "thumb_out": 0.5,
        "index_up": 1.0, "middle_up": 1.0, "ring_up": 0.6, "pinky_up": 1.0, "index_hook": 0,
    },
    "eight_thumb_middle": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.3, "thumb_out": 0.5,
        "index_up": 1.0, "middle_up": 0.6, "ring_up": 1.0, "pinky_up": 1.0, "index_hook": 0,
    },
    "nine_thumb_index_in": {
        "right_shoulder_angle": -60, "right_elbow_angle": -40,
        "finger_spread": 0.3, "thumb_out": 0.5,
        "index_up": 0.6, "middle_up": 1.0, "ring_up": 1.0, "pinky_up": 1.0, "index_hook": 0,
    },
}
