from manim import *
class WindmillScene(Scene):
    CONFIG={
        'dot_config':{
            'radius':0.07,
            'color':BLUE,
        },
        'n_points':16,
    }
    def construct(self):
        dots=self.add_points()[0]
        line=self.get_windmill(self.add_points()[1])
        dot_pivot=self.get_pivot_dot(line,)
        next_pivot,angle=self.next_pivot_angle(line)
        self.play(
            LaggedStartMap(Create,dots)
        )
        self.play(Create(line),DrawBorderThenFill(dot_pivot))
        self.play(
            Rotate(line,angle=angle)
        )
        self.wait()
    def get_windmill(self,points,pivot=None,angle=TAU/6):
        line=Line(LEFT,RIGHT)
        line.set_length(2*config['frame_width'])
        line.set_angle(angle)
        line.point_set=points
        if pivot is not None:
            line.pivot=pivot
        else:
            line.pivot=points[0]
        line.rot_speed=0.25
        line.add_updater(
            lambda l: l.move_to(l.pivot)
        )
        return line
    def add_points(self):
        points=self.get_random_point_set(16)
        dots=self.get_dots(points)
        return [dots,points]
    def get_random_point_set(self,n_points=11,width=6,height=6):
        return np.array([
            [
                -width/2+np.random.random()*width,
                -height/2+np.random.random()*height,
                0
            ]
            for _ in range(n_points)
        ])
    def get_dots(self,points):
        return VGroup(*[
            Dot(**self.CONFIG['dot_config']).move_to(point) for point in points
        ])
    def get_pivot_dot(self,windmill,color=YELLOW):
        pivot_dot=Dot(color=color)
        pivot_dot.add_updater(
            lambda d: d.move_to(windmill.pivot)
        )
        return pivot_dot
    def next_pivot_angle(self,windmill):
        curr_angle=windmill.get_angle()
        non_pivot=list(
            filter(
                lambda p: not np.all(p==windmill.pivot),windmill.point_set
            )
        )
        angles=np.array([
            -(angle_of_vector(point-windmill.pivot)-curr_angle)%PI
            for point in non_pivot
        ])
        tiny_indices=angles<1e-6
        if np.all(tiny_indices):
            return non_pivot[0], PI
        angles[tiny_indices]=np.inf
        index=np.argmin(angles)
        return non_pivot[index],angles[index]