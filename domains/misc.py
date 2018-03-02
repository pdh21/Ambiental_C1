import numpy as np

def find_nearest(array, value):
    ''' Find nearest value is an array '''
    idx=np.empty((value.size))
    for i in range(0,value.size):
        idx[i] = (np.abs(array-value[i])).argmin()
    return idx.astype('int')

def gradient(xnew,ynew,pix_dist,pixel_width,pixel_height,xpix,ypix,points,c):
    for j in range(xnew.shape[0] - 1):

        dy=ynew[j+1]-ynew[j]
        dx=xnew[j+1]-xnew[j]
        angle=0.5*np.pi-np.arctan(dy/dx)
        t_x=pix_dist*pixel_width*np.cos(angle)
        t_y=pix_dist*pixel_height*np.sin(angle)
        #inner value
        x_in=find_nearest(xpix,xnew[j]+t_x)
        y_in=find_nearest(ypix,ynew[j]+t_y)
        #outer value
        x_out=find_nearest(xpix,xnew[j]-t_x)
        y_out=find_nearest(ypix,ynew[j]-t_y)
        points[c,:]=[(np.max(arr[y_out,x_out])-np.max(arr[y_in,x_in]))/dx,xnew[j],ynew[j]]
        c+=1

