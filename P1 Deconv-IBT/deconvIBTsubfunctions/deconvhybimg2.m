function deconvresult=deconvhybimg2(imgraw,n_itr,file_h)
%0.076 was ps
ps =0.058;     % sensor pixel size (um)%was 2
intp = 1;       % interpolation ratio (for raw image only, PSF should be high-resolution in the first place.)
Bkg_S = 0;      % background subtraction on raw image or not (1:yes, 0:no)

%read image to be deconvolved
file_img=imgraw;
Img=uint16(file_img);
Img = mean(Img,3);       % use the intensity
if Bkg_S == 1
    [n,xout] = hist(Img(:),100);
    bkg_I = mean(xout(n==max(n)));
    Img = Img - bkg_I;      % substract the background
end

[Hm Wm] = size(Img);
xm = (0:Wm-1)*ps;
ym = (0:Hm-1)*ps;

% prepare h
%  h = double(imread(file_h));
 h=file_h;
border_h = [h(1,1:end-1),(h(1:end-1,end))',h(end,2:end),(h(2:end,1))'];
[n,xout] = hist(border_h,length(border_h));
bkg_h = mean(xout(n==max(n)));
h = h-bkg_h;
h = h./sum(h(:));   % normalize 
h = padarray(h,[intp-1 intp-1],0,'post');    % pad the PSF to make the matrix dimension = intp*N

%perform Lucy Richardson Deconvolution
% WT = zeros(size(Imgb));
% WT(5:end-4,5:end-4) = 1;

DampTh = 0;     % threshold for damping   
Imgb = interp2(xm,ym,Img,xm(1):ps/intp:xm(end),(ym(1):ps/intp:ym(end))');
J = deconvlucy({Imgb},h,n_itr,DampTh);
% [J lagra]= deconvreg({Imgb},h,0);
%  [J,ps]= deconvblind({Imgb},h,10);
deconvresult=J{2};

end

