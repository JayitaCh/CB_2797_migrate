import numpy as np

class Radar(object):
    # https://medium.com/@reinapeh/creating-a-complex-radar-chart-with-python-31c5cc4b3c5c
    def __init__(self, figure, title, labels, rect=None):
        if rect is None:
            rect = [0.05, 0.05, 1, 1]

        self.n = len(title)
        self.angles = np.arange(0, 360, 360.0/self.n)
        
        self.axes = [figure.add_axes(rect, projection='polar', label='axes%d' % i) for i in range(self.n)]
        self.ax = self.axes[0]
        self.ax.set_thetagrids(self.angles,labels=[])
        for angle, label in zip(self.angles, title):
            angle_rad = np.deg2rad(angle)
            self.ax.text(
                angle_rad, 14.0,  # outside the radar circle
                label,
                ha='center',
                va='center',
                fontsize=11,
                fontname="DejaVu Sans",
                zorder=9
            )
        # self.ax.set_thetagrids(self.angles, labels=title, fontsize=11,fontname="DejaVu Sans", zorder=0) # Feature names
        self.ax.set_yticklabels([])
        
        for ax in self.axes[1:]:
            ax.xaxis.set_visible(False)
            ax.set_yticklabels([])
            ax.set_zorder(-99)

        for ax, angle, label in zip(self.axes, self.angles, labels):
            ax.spines['polar'].set_color('black')
            ax.spines['polar'].set_zorder(99)
            # angle_deg = np.degrees(angle)
            # ha = 'left' if 90 < angle_deg < 270 else 'right'
            # ax.text(angle, ax.get_rmax() + 0.5, label, size=12, horizontalalignment=ha, verticalalignment='center')
                     
    def plot(self, values, *args, **kw):
        angle = np.deg2rad(np.r_[self.angles, self.angles[0]])
        values = np.r_[values, values[0]]
        self.ax.plot(angle, values,marker='o', markersize=8,*args, **kw)
        kw['label'] = '_noLabel'
        self.ax.fill(angle, values,zorder=-99,*args,**kw)