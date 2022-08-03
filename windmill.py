from manim import *
import itertools as it
class WindmillScene(Scene):
    CONFIG={
        'dot_config':{
            'radius':0.07,
            'color':BLUE,
        },
        'n_points':16,
        'leave_shadows':False,
        'colors_flash':[RED,GREEN,TEAL]
    }
    def construct(self):
        points=self.get_random_point_set(16)
        dots=self.get_dots(points)
        line=self.get_windmill(points)
        dot_pivot=self.get_pivot_dot(line)
        next_pivot,angle=self.next_pivot_angle(line)
        self.play(
            LaggedStartMap(Create,dots)
        )
        self.play(Create(line),DrawBorderThenFill(dot_pivot))
        self.switch_pivots(line)
        # self.play(
        #     Rotate(line,angle=angle)
        # )
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
    def rotate_to_next_pivot(self,windmill,max_time=None,added_anims=None):
        new_pivot,angle=self.next_pivot_angle(windmill)
        change_pivot_at_end=True
        if added_anims is None:
            added_anims=[]
        run_time=angle/windmill.rot_speed
        if max_time is not None and run_time>max_time:
            ratio=max_time/run_time
            rate_func=(lambda t:t*ratio)
            run_time=max_time
            change_pivot_at_end=False
        else:
            rate_func=linear
        for anim in added_anims:
            if anim.run_time>run_time:
                anim.run_time=run_time
        self.play(Rotate(
            windmill,-angle,rate_func=rate_func,run_time=run_time
        ),*added_anims)
        return [self.get_hit_flash(new_pivot)], run_time
    def get_hit_flash(self,point):
        color_flash=it.cycle(self.CONFIG['colors_flash'])
        flash=Flash(
            point,
            line_length=.1,
            flash_radius=.2,
            run_time=0.5,
            remove=True
        )
        flash_mob=flash.mobject
        for submob in flash_mob:
            submob.reverse_points()
            submob.set_color(next(color_flash))
        return Uncreate(flash.mobject,run_time=0.5,lag_ratio=0)
    def switch_pivots(self,windmill):
        self.rotate_to_next_pivot(windmill)
        flashes,run_time=self.rotate_to_next_pivot(windmill)
        self.play(*flashes)
        self.let_windmill_run(windmill,10)
    def let_windmill_run(self,windmill,time):
        anims_from_last_hit=[]
        while time>0:
            anims_from_last_hit,last_run_time=self.rotate_to_next_pivot(
                windmill,
                max_time=time,
                added_anims=anims_from_last_hit
            )
            time-=last_run_time