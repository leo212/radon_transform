import numpy as np

def ffft(x,alpha):
    # y=ffft(x,alpha)
    # fast algorithm for the fractional fft
    # inputs:
    # x - the input vector
    # alpha - the scaling coefficient
    # Ofer Levi - Jan 21 2012
    x=x[:]
    x=np.fft.fftshift(x) #  centering x indices arround zero
    n=len(x)
    E=1j*np.pi*alpha/n
    ivec=np.transpose(np.arange(-(n/2),(n/2)))
    Dd=np.exp(-E*ivec*ivec)
    Dx=Dd*x    # multiplication with the appropriate diagonal matrix of complex exponnentials
    z=np.concatenate((Dx,np.zeros(n,dtype='float64')))  #  zero padding
    ivec2=(np.arange(0,n,dtype='float64')).transpose()
    T1stCol=np.exp(E*ivec2*ivec2)   #  1st column of the Toeplitz matrix
    C1stCol=np.concatenate((T1stCol,[0],np.flipud(T1stCol[1:n]))) #  1st column of the circulant matrix

    D2d=np.fft.fft(C1stCol)/np.sqrt(n)   #  applying normalyzed fft to the first column of C

    Fz=np.fft.fft(z)
    D2Fz=D2d*Fz  #
    Cz=np.fft.ifft(D2Fz) # the convolution result of z and the 1st column of C (which is equivalent to C*z)

    TDx=Cz[0:n]  #  ommiting the last n entries of Cz
    y=Dd*TDx     # Left multiflication with the appropriate diagonal matrix
    return y
    # written by Ofer Levi 18/4/2007


def ffft2(x,alpha):
    m=len(x)
    n=2*m
    t=np.zeros(n,dtype='complex')
    y=np.zeros(n,dtype='complex')
    j=np.arange(0,m,dtype='float64')

    y[0:m]=x*np.exp(1j*np.pi*alpha*(j-j*j/m))

    t[0:m]=np.exp(-1j*np.pi*alpha/m*j*j)
    t[m+1:2*m]=np.flip(t[1:m],0)

    t=np.fft.fft(np.conj(t))

    y=np.fft.fft(y)*t
    y=np.fft.ifft(y)

    y=y[0:m]*np.exp(1j*np.pi*alpha*(j-m/2-j*j/m))
    return y

def PPFFT(X):
    n = len(X)
    Y = np.zeros((2*n,2*n),dtype='complex')

    # Basically Horizontal Lines
    PaddedX=np.concatenate((np.zeros((n/2,n)),X,np.zeros((n/2,n))))
    Z=np.fft.fftshift(PaddedX,0)
    Z=np.fft.fft(Z,axis=0)
    Z=np.fft.fftshift(Z,0)

    for r in range(0,n):
        alpha=float(n-r)/n
        t = ffft2(Z[r,:],alpha)
        Y[0:n,r] = t.transpose()
        alpha=float(-r)/n
        t = ffft2(Z[r+n,:],alpha)
        Y[0:n,r+n] = t.transpose()

    PaddedX=np.hstack((np.zeros((n,n/2)),X,np.zeros((n,n/2)))).transpose()
    Z=np.fft.fftshift(PaddedX,0)
    Z=np.fft.fft(Z,axis=0)
    Z=np.fft.fftshift(Z,0)

    Z=np.vstack((Z[1:2*n,:], Z[0,:])) #Move left edge to right edge to include the right border edges
    for r in range(0,n):
        alpha=float(n-r)/n
        t = ffft2(Z[2*n-r-1,:],alpha)
        Y[n:2*n,r] = t.transpose()
        alpha=float(-r)/n
        t = ffft2(Z[n-r-1,:],alpha)
        Y[n:2*n,r+n] = t.transpose()

    Y = Y/(np.sqrt(2)*n)  # Normalization
    return Y

def FSS(X, n):
    P = PPFFT(X).transpose()
    P = np.fft.fftshift(P,axes=0)
    P = np.fft.ifft(P,axis=0)
    P = np.fft.fftshift(P,axes=0)
    S = np.real(P)*2*n
    return S

def Adj_PPFFT(Y):
    m = len(Y)
    n = int(m/2)

    X0=np.zeros((m,n),dtype='complex')
    X1=np.zeros((m,n),dtype='complex')

    Y = Y * (np.sqrt(2)*n)

    Y0=Y[0:n,:]
    Y1=Y[n:m,:]

    for r in range(0,n):
        alpha=float(n-r)/n
        t = ffft2(Y0[:,r].transpose(),-alpha)
        X0[r,:] = t

        alpha=float(-r)/n
        t= ffft2(Y0[:,r+n].transpose(),-alpha)
        X0[r+n,:] = t

    X0=np.fft.fftshift(X0,axes=0)
    X0=np.fft.ifft(X0,axis=0) #,[],1)
    X0=np.fft.fftshift(X0,axes=0)

    for r in range(0,n):
        alpha=float(n-r)/n
        t = ffft2(Y1[:,r].transpose(),-alpha)
        X1[m-r-1,:]=t

        alpha=float(-r)/n
        t = ffft2(Y1[:,n+r].transpose(),-alpha)
        X1[n-r-1,:]=t

    X1 = np.vstack((X1[m-1,:].reshape((1,n)), X1[0:m-1,:]))
    X1 = np.fft.fftshift(X1,axes=0)
    X1 = np.fft.ifft(X1,axis=0) #,[],1)
    X1 = np.fft.fftshift(X1,axes=0).transpose()
    X1 = X1[:,n/2:3*n/2]
    X0 = X0[n/2:3*n/2,:]
    X = (X0+X1)/n

    return X

def Adj_FSS(S, n):
    m=n*2
    P=np.fft.fftshift(S,axes=0)
    P=np.fft.fft(P,axis=0)
    P=np.fft.fftshift(P,axes=0)
    X=np.real(Adj_PPFFT(P.transpose()))
    return X


from scipy import sparse
from scipy import misc
from . import radon_sss
import matplotlib.pyplot as plt
import time

def test_accuracy(filename, row, rows):
    x = misc.imread(filename, flatten=True).astype('float64')
    n = np.shape(x)[0]

    start = time.time()
    y1 = radon_sss.slow_slant_stack(x, n)
    duration = time.time() - start
    print("FSS took:" + str(duration * 1000) + "ms")

    start = time.time()
    y2 = FSS(x, n)
    duration = time.time() - start
    print("PSFSS took:" + str(duration * 1000) + "ms")

    X = np.reshape(x, (n * n))
    Y = np.reshape(y2, (4 * n * n))

    def mv(v):
        image = np.reshape(v, (n,n))
        radon = FSS(image, n)
        result = np.reshape(radon, 4*n*n)
        return result

    def rmv(v):
        image = np.reshape(v, (2*n,2*n))
        radon = Adj_FSS(image, n)
        result = np.reshape(radon, n*n)
        return result

    A = sparse.linalg.LinearOperator((4*n*n,n*n), matvec=mv, rmatvec=rmv)
    AT = sparse.linalg.LinearOperator((n*n,4*n*n), matvec=rmv, rmatvec=mv)

    start = time.time()
    XCG = sparse.linalg.cg(AT*A, AT*Y)[0]
    duration = time.time() - start
    print("Solving using Conjugate Gradient took:" + str(duration * 1000) + "ms")

    start = time.time()
    XC2 = sparse.linalg.lsqr(A, Y)[0]
    duration = time.time() - start
    print("Solving using Iterative Least Squares took:" + str(duration * 1000) + "ms")

    xc = np.reshape(XC2, (n, n))
    xcg = np.reshape(XCG, (n, n))
    # rc = np.reshape(A * XC2, (n , n))

    ls_diff = np.abs(xc - x) / 255
    cg_diff = np.abs(xcg - x) / 255

    plt.subplot(rows, 4, (row-1)*4+1)
    plt.xlabel("Source Image (X)")
    plt.imshow(x, cmap='gray', vmin=0, vmax=255)
    plt.subplot(rows, 4, (row-1)*4+2)
    plt.xlabel("Radon Transform (SSS)")
    plt.imshow(y1, cmap='gray')
    plt.subplot(rows, 4, (row-1)*4+3)
    plt.xlabel("Reconstruct image \n using Least Squares")
    plt.imshow(xc, cmap='gray')
    plt.subplot(rows, 4, (row-1)*4+4)
    plt.xlabel("Reconstruct image \n using Conjugate Gradient")
    plt.imshow(xcg, cmap='gray', vmin=0, vmax=255)
    # plt.subplot(rows, 4, (row-1)*4+4)
    # plt.xlabel("Radon Transform (PSFSS)")
    # plt.imshow(y2, cmap='gray')

    # print filename+ ": CG Error:" + str(np.abs(np.linalg.norm(xcg)-np.linalg.norm(x))/n)
    # print filename+ ": LS Error:" + str(np.abs(np.linalg.norm(xc)-np.linalg.norm(x))/n)
    print("Sum of error LS reconstruction:" + str(sum(sum(ls_diff))))
    print("Sum of error CG reconstruction:" + str(sum(sum(cg_diff))))

    # plt.show()

# test_accuracy("SheppLogan_Phantom.png",1,1)
# test_accuracy("lenna100x100.png",2,5)
# test_accuracy("simple_lines100x100.png",3,5)
# test_accuracy("simple_lines_negative100x100.png",4,5)
# test_accuracy("simple_lines_noise100x100.png",5,5)
# plt.show()

def testFss(image):
    image = misc.imread(image, flatten=True).astype('float64')
    n = np.shape(image)[0]

    start = time.time()
    radon0 = FSS(image, n)
    duration =  time.time() - start
    print("FSS took:" + str(duration*1000) + "ms")

    # Plot the original and the radon transformed image
    plt.subplot(2, 1, 1), plt.imshow(image, cmap='gray')
    plt.xticks([]), plt.yticks([])
    plt.xlabel("Original Image")
    plt.subplot(2, 1, 2), plt.imshow(radon0, cmap='gray')
    plt.xticks([]), plt.yticks([])
    plt.xlabel("FSS Radon")

    plt.show()

# testFss("simple_lines_negative100x100.png")
