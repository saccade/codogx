"""Matplotlib stills when the optional Manim renderer is unavailable. Codex."""
import io
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from ring import state_at, shaft, torque_about_shaft, follow_flux, capture, pose, winding
from display_units import selection, words, scaled

BLUE,RED,COPPER,GREEN='#24489c','#a85147','#9a6241','#528b7b'


def picture(fig,pixels):
    buffer=io.BytesIO()
    fig.savefig(buffer,format='png',dpi=pixels/11,facecolor='#f8f7f2')
    plt.close(fig);buffer.seek(0)
    with Image.open(buffer) as im:return im.copy()


def projected(points):
    return np.asarray(points)@np.array([[1,.10],[.40,.32],[0,.95]])


def draw_ring(ax,case,points,area,forces=None):
    p=projected(points)
    ax.plot(p[:,0],p[:,1],color=COPPER,lw=.7)
    axis=projected(np.array([-1.6*shaft(case),1.6*shaft(case)]))
    ax.plot(axis[:,0],axis[:,1],color='#999999')
    arrow=projected(area/np.linalg.norm(area))
    ax.arrow(0,0,*arrow,width=.015,color=BLUE,length_includes_head=True)
    if forces is not None:
        indices=np.linspace(0,len(points)-1,40,dtype=int)
        f=projected(forces[indices])*.1
        ax.quiver(p[indices,0],p[indices,1],f[:,0],f[:,1],angles='xy',scale_units='xy',scale=1,color=RED,width=.003)
    ax.set_aspect('equal');ax.set(xlim=(-1.8,1.8),ylim=(-1.5,1.5));ax.axis('off')


class RingView:
    def __init__(self,pixels=1100,units=None):
        self.pixels=pixels;self.display_units=selection(units)
    def still(self,case,time=0,forces=True):
        st=state_at(case,time)
        fig,ax=plt.subplots(1,2,figsize=(11,6.2),layout='constrained')
        draw_ring(ax[0],case,st.forces.positions,st.flux.area,
                  st.forces.per_length if forces else None)
        ax[0].set_title('Forces along the wire',color=BLUE)
        p=st.forces.positions
        ax[1].plot(p[:,0],p[:,1],color=COPPER,lw=.7)
        ax[1].set_aspect('equal');ax[1].axis('off');ax[1].set_title('Signed shadow along the field',color=RED)
        for a,tau in [(ax[0],torque_about_shaft(case,st.forces.moment)),(ax[1],st.flux.torque)]:
            a.text(.5,-.04,'shaft torque: '+words(tau,'torque',self.display_units),transform=a.transAxes,ha='center',fontsize=10)
        fig.suptitle(f'{case.windings} windings · linked flux '+words(st.flux.linked,'flux',self.display_units))
        return picture(fig,self.pixels)


class CaptureView:
    def __init__(self,pixels=1100,units=None):
        self.pixels=pixels;self.display_units=selection(units)
    def still(self,case,angle=np.arccos(4/5)):
        from capture_view import reading,sentences
        r=reading(case,angle);a=np.linspace(0,2*np.pi,241)
        fig,ax=plt.subplots(1,2,figsize=(11,6.2))
        points=pose(winding(case)[0],case,angle)
        draw_ring(ax[0],case,points,follow_flux(case,angle).area)
        ax[0].set_title('The ring on its shaft',color=BLUE)
        ax[1].plot(scaled(a,'angle',self.display_units),
                   [scaled(follow_flux(case,x).linked,'flux',self.display_units) for x in a],color=GREEN,label='linkage')
        other=ax[1].twinx()
        other.plot(scaled(a,'angle',self.display_units),
                   [scaled(capture(case,x),'capture',self.display_units) for x in a],color=RED,label='capture')
        ax[1].axvline(scaled(angle,'angle',self.display_units),color='#999999',ls='--')
        ax[1].set(xlabel='angle ('+self.display_units['angle']+')',ylabel='linkage ('+self.display_units['flux']+')')
        other.set_ylabel('capture ('+self.display_units['capture']+')',color=RED)
        ax[1].grid(alpha=.15);ax[1].set_title('Linkage and capture',color=RED)
        lines=sentences(case,r,self.display_units)
        fig.subplots_adjust(bottom=.29,wspace=.4)
        for n,key in enumerate(['linkage','capture','torque','voltage','balance']):
            fig.text(.05,.21-.036*n,lines[key],fontsize=9)
        return picture(fig,self.pixels)
