clear all;close all;clc;


zvis=2;
zstart=1;
zend=5;

tsStack = tiffstackloading('Imset1-Gold-Current2pA.tif');
%fname = 'C:\Users\ahmet\Documents\MATLAB\mathMIBIdata\04082019deconv\SUM_mbrducell1x-2.tif';


%tsStack = TIFFStack('Imset1-Gold-Current2pA.tif');
% imagesc(abs(tsStack(:,:,zvis)));colormap(gray(256));axis image
[rows, columns, numSlices] = size(tsStack);
outputImage = zeros(rows, columns); % Or whatever class you want.
outKer = nonIsotropicGaussianPSF([3 3 3],3,'single');

for i= zstart : zend
    
    outputImage=imadd(outputImage,double(tsStack(:,:,i)));
        
end
figure;imagesc(outputImage);colormap('gray');axis image
niteration=17;
Image1proc=deconvhybimg2(outputImage,niteration,outKer(:,:,9));
figure;imagesc(Image1proc);colormap('gray');axis image

imwrite2tif(outputImage,[],'C:\Users\ahmet\Documents\MATLAB\mathMIBIresults\AuResscansSets12\Im1set1Au2pARaw.tif','uint16');
imwrite2tif(Image1proc,[],'C:\Users\ahmet\Documents\MATLAB\mathMIBIresults\AuResscansSets12\Im1set1Au2pADeconv.tif','uint16');

% Image1proc=outputImage;
Reslist=zeros(1,3);
figure;
for i=1:3
    
    
if i==1
   ROI=[65 65 30 30];
xsec = [5 26];
ysec = [26 5];
end
if i==2
ROI=[99 99 30 30];
xsec = [5 26];
ysec = [26 5];

end
if i==3
ROI=[135 135 30 30];
xsec = [5 26];
ysec = [26 5];
end


imageforres2=imcrop(Image1proc,ROI);

% figure;imagesc(imageforres2);colormap('gray');axis image

%average 10 neighbors
c=zeros;
for mm=[-4:5]
c=improfile(imageforres2,xsec+mm,ysec+mm)+c;
end
c=c./10;

% figure;scatter(1:size(c),c(:),'filled');hold on;plot(c);grid on;
sizeimraw=size(c);
sizeimrawX=sizeimraw(1);

xqsec = 1:0.25:max(xsec);
cq2 = interp1(min(xsec):max(xsec),c',xqsec);
% plot(xqsec,cq2,':.');
sizeimintp=size(cq2);
sizeimintpX=sizeimintp(2);

pixelsize=78;
intpixelsize=pixelsize/(sizeimintpX/sizeimrawX)
px=round(intpixelsize);

[maxval,maxpos]=max(cq2(:));
[minval,minpos]=min(cq2(:));
cq2up=cq2(maxpos:minpos+1);
sizeimfin=size(cq2up);
%   axis square;
  
subplot(3,1,i);
% plot(cq2,'k','LineWidth',2);grid on;
% size(cq2)
plot(cq2up,'k','LineWidth',2);grid on;
size(cq2up)



%linescans(i)=cq2up;

xlabel('Line scan (nm)','FontSize', 16)
ylabel('^{197}Au channel counts','FontSize', 16)

% set(gca, 'Xdir', 'reverse')
 set(gca,'XTickLabel',{num2str(0*px);num2str(2*px);num2str(4*px);num2str(6*px);num2str(8*px);num2str(10*px);num2str(12*px);num2str(14*px)})
uplimit=maxval*0.84;
[ResX1 Cq84] = min(abs(cq2up-uplimit));
downlimit=maxval*0.16;
[ResX2 Cq16] = min(abs(cq2up-downlimit));
IonRes=(Cq16-Cq84)*intpixelsize
Reslist(i)=IonRes
hold on;
x1 = 8;
y1 = 200;
txt1 = ['Res = ',num2str(IonRes),' nm'];
text(x1,y1,txt1,'FontSize', 16)
%figure;imagesc(imageforres2);colormap('gray');axis image
%line(xsec, ysec,'Color','r','LineWidth',4)
end

set(gcf, 'Position', get(0, 'Screensize'));

saveaspub(gcf,'C:\Users\ahmet\Documents\MATLAB\mathMIBIresults\AuResscansSets12\set1d132pasum\3plotFchanResolutionImage3subplots','png')


% Image1proc=outputImage;
%Reslist=zeros(1,3);
figure;
for i=1:3
    
    
if i==1
   ROI=[65 65 30 30];
xsec = [5 26];
ysec = [26 5];
end
if i==2
ROI=[99 99 30 30];
xsec = [5 26];
ysec = [26 5];

end
if i==3
ROI=[135 135 30 30];
xsec = [5 26];
ysec = [26 5];
end


imageforres2=imcrop(Image1proc,ROI);

% figure;imagesc(imageforres2);colormap('gray');axis image

%average 10 neighbors
c=zeros;
for mm=[-4:5]
c=improfile(imageforres2,xsec+mm,ysec+mm)+c;
end
c=c./10;

% figure;scatter(1:size(c),c(:),'filled');hold on;plot(c);grid on;
sizeimraw=size(c);
sizeimrawX=sizeimraw(1);

xqsec = 1:0.25:max(xsec);
cq2 = interp1(min(xsec):max(xsec),c',xqsec);
% plot(xqsec,cq2,':.');
sizeimintp=size(cq2);
sizeimintpX=sizeimintp(2);

pixelsize=78;
intpixelsize=pixelsize/(sizeimintpX/sizeimrawX)
px=round(intpixelsize);

[maxval,maxpos]=max(cq2(:));
[minval,minpos]=min(cq2(:));
cq2up=cq2(maxpos:minpos+1);
sizeimfin=size(cq2up);
%   axis square;
  
subplot(3,1,i);
[w, x0, fitresult,xData, yData, gof] = simsEdge(21:100,cq2(21:100))
h = plot( fitresult, xData, yData );
legend( h, 'Ion Data', 'Erf fit', 'Location', 'NorthEast' );
hold on;
axis([-5 80 -0.2 1.2])




%linescans(i)=cq2up;

xlabel('Line scan (nm)','FontSize', 16)
ylabel('^{197}Au channel counts','FontSize', 16)

% set(gca, 'Xdir', 'reverse')
set(gca,'XTickLabel',{num2str(0*px);num2str(10*px);num2str(20*px);num2str(30*px);num2str(40*px);
    num2str(50*px);num2str(60*px);num2str(70*px);num2str(80*px)})
uplimit=maxval*0.84;
[ResX1 Cq84] = min(abs(cq2up-uplimit));
downlimit=maxval*0.16;
[ResX2 Cq16] = min(abs(cq2up-downlimit));
IonRes2=w*intpixelsize
Reslist2(i)=IonRes2
hold on;
x1 = 0;
y1 = 0.5;
txt1 = ['Res = ',num2str(IonRes2),' nm'];
text(x1,y1,txt1,'FontSize', 16)
%figure;imagesc(imageforres2);colormap('gray');axis image
%line(xsec, ysec,'Color','r','LineWidth',4)
end

Reslist
meanRes=mean(Reslist)
stdRes=std(Reslist)
figure;
for i=1:3
  
    
if i==1
   ROI=[65 65 30 30];
xsec = [5 26];
ysec = [26 5];
end
if i==2
ROI=[99 99 30 30];
xsec = [5 26];
ysec = [26 5];

end
if i==3
ROI=[135 135 30 30];
xsec = [5 26];
ysec = [26 5];
end

imageforres2=imcrop(Image1proc,ROI);
% figure;imagesc(imageforres2);colormap('gray');axis image
% line(xsec,ysec,'Color','m','LineWidth',2)

%average 10 neighbors
c=zeros;
for kkk=[-4:5]
c=improfile(imageforres2,xsec+kkk,ysec+kkk)+c;
end
c=c./10;
% figure;plot(c);grid on;
sizeimraw=size(c);
sizeimrawX=sizeimraw(1);



xqsec = 1:0.25:max(xsec);
cq2 = interp1(min(xsec):max(xsec),c',xqsec);
%  figure;plot(xqsec,cq2,':.');
sizeimintp=size(cq2);
sizeimintpX=sizeimintp(2);

pixelsize=78;
intpixelsize=pixelsize/(sizeimintpX/sizeimrawX);
px=round(intpixelsize);

[maxval,maxpos]=max(cq2(:));
[minval,minpos]=min(cq2(:));
cq2up=cq2(maxpos:minpos+1);
%  figure;plot(cq2up);axis square;
sizeimfin=size(cq2up);
if i==1
colplot=plot(cq2up,'m','LineWidth',2);grid on;hold on;
end
if i==2
colplot=plot(cq2up,'g','LineWidth',2);grid on;hold on;
end
if i==3
colplot=plot(cq2up,'b','LineWidth',2);grid on;hold on;
end

end


xlabel('Line scan (nm)','FontSize', 30)
xt = get(gca, 'XTick');
set(gca, 'FontSize', 20)
ylabel('^{197}Au Channel counts','FontSize', 30)

% set(gca, 'Xdir', 'reverse')
set(gca,'XTickLabel',{num2str(0*px);num2str(2*px);num2str(4*px);num2str(6*px);num2str(8*px);num2str(10*px);num2str(12*px);num2str(14*px)})
axis square
set(gcf, 'Position', get(0, 'Screensize'));



x1 = 6;
y1 = 270;
txt1 = ['Resolution = ',num2str(round(meanRes)),' nm'];
text(x1,y1,txt1,'FontSize', 30)
x2 = 6;
y2 = 240;
txt2 = ['SD = ',num2str(round(stdRes)),' nm'];
text(x2,y2,txt2,'FontSize', 30)
%set(gca,'Color','g');

% saveTightFigure('3plotFchanResolution.png');
saveaspub(gcf,'C:\Users\ahmet\Documents\MATLAB\mathMIBIresults\AuResscansSets12\set1d132pasum\3plotFchanResolution','png')


% ROI=[91 185 30  30];
% xsec = [1 12];
% ysec = [18 18];  

figure;imshow(Image1proc,[0 1000]);colormap('gray');axis image
line(xsec+65, ysec+65,'Color','m','LineWidth',2)
line(xsec+100, ysec+100,'Color','g','LineWidth',2)
line(xsec+135, ysec+135,'Color','b','LineWidth',2)
saveaspub(gcf,'C:\Users\ahmet\Documents\MATLAB\mathMIBIresults\AuResscansSets12\set1d132pasum\3plotFchanResolutionImageLines','png')


Reslist
meanRes=mean(Reslist2)
stdRes=std(Reslist2)
figure;
for i=1:3
  
    
if i==1
   ROI=[65 65 30 30];
xsec = [5 26];
ysec = [26 5];
end
if i==2
ROI=[99 99 30 30];
xsec = [5 26];
ysec = [26 5];

end
if i==3
ROI=[135 135 30 30];
xsec = [5 26];
ysec = [26 5];
end

imageforres2=imcrop(Image1proc,ROI);
% figure;imagesc(imageforres2);colormap('gray');axis image
% line(xsec,ysec,'Color','m','LineWidth',2)

%average 10 neighbors
c=zeros;
for kkk=[-4:5]
c=improfile(imageforres2,xsec+kkk,ysec+kkk)+c;
end
c=c./10;
% figure;plot(c);grid on;
sizeimraw=size(c);
sizeimrawX=sizeimraw(1);



xqsec = 1:0.25:max(xsec);
cq2 = interp1(min(xsec):max(xsec),c',xqsec);
%  figure;plot(xqsec,cq2,':.');
sizeimintp=size(cq2);
sizeimintpX=sizeimintp(2);

pixelsize=78;
intpixelsize=pixelsize/(sizeimintpX/sizeimrawX);
px=round(intpixelsize);

[maxval,maxpos]=max(cq2(:));
[minval,minpos]=min(cq2(:));
cq2up=cq2(maxpos:minpos+1);
%  figure;plot(cq2up);axis square;
sizeimfin=size(cq2up);
if i==1
[w, x0, fitresult,xData, yData, gof] = simsEdge(35:80,cq2(35:80))
h = plot( fitresult,'m', xData, yData,'mo' );hold on;
legend( h, 'Ion Data', 'Erf fit', 'Location', 'NorthEast' );

%colplot=plot(fitresult,'m','LineWidth',2);grid on;hold on;

end
if i==2
[w, x0, fitresult,xData, yData, gof] = simsEdge(35:80,cq2(35:80))
h = plot( fitresult,'g', xData, yData,'go' );hold on;
legend( h, 'Ion Data', 'Erf fit', 'Location', 'NorthEast' );
%colplot=plot(fitresult,'g','LineWidth',2);grid on;hold on;
end
if i==3
[w, x0, fitresult,xData, yData, gof] = simsEdge(40:85,cq2(40:85))  
h = plot( fitresult,'b', xData, yData,'bo' );hold on;
legend( h, 'Ion Data', 'Erf fit', 'Location', 'NorthEast' );
%colplot=plot(fitresult,'b','LineWidth',2);grid on;hold on;
end

end


xlabel('Line scan (nm)','FontSize', 30)
xt = get(gca, 'XTick');
set(gca, 'FontSize', 20)
ylabel('^{197}Au Channel counts','FontSize', 30)
axis([-5 55 -0.2 1.2])

% set(gca, 'Xdir', 'reverse')
set(gca,'XTickLabel',{num2str(0*px);num2str(10*px);num2str(20*px);num2str(30*px);num2str(40*px);num2str(50*px)})
axis square
set(gcf, 'Position', get(0, 'Screensize'));



x1 = 0;
y1 = 0.4;
txt1 = ['Res = ',num2str(round(meanRes)),' nm'];
text(x1,y1,txt1,'FontSize', 30)
x2 = 0;
y2 = 0.3;
txt2 = ['SD = ',num2str(round(stdRes)),' nm'];
text(x2,y2,txt2,'FontSize', 30)
%set(gca,'Color','g');

% saveTightFigure('3plotFchanResolution.png');
saveaspub(gcf,'C:\Users\ahmet\Documents\MATLAB\mathMIBIresults\AuResscansSets12\set1d132pasum\3plotFchanResolution','png')


% ROI=[91 185 30  30];
% xsec = [1 12];
% ysec = [18 18];  

figure;imshow(Image1proc,[0 1000]);colormap('gray');axis image
line(xsec+65, ysec+65,'Color','m','LineWidth',2)
line(xsec+100, ysec+100,'Color','g','LineWidth',2)
line(xsec+135, ysec+135,'Color','b','LineWidth',2)
saveaspub(gcf,'C:\Users\ahmet\Documents\MATLAB\mathMIBIresults\AuResscansSets12\set1d132pasum\3plotFchanResolutionImageLines','png')

