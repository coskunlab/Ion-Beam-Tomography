clear all;close all;clc;

%3D IBT SLICES
% zvis=293;
zstart=1;
zend=740;

%3D IBT RAW DATA
tsStack = TIFFStack('\IBTdata\chromatin\iduchromatin-allslices.tif');

%THIS IS CALCULATED POINT SPREAD FUNCTION BASED ON ION BEAM WIDTH
outKer = nonIsotropicGaussianPSF([4 4 4],3,'single');
% outKer = nonIsotropicGaussianPSF([5 5 5],3,'single');

%SETTING THE SLIDING WINDOW TO BE 5, CAN BE CHANGED TO 10 OR 20
intv=5;
for i=zstart:zend
    zvis=i;
    
% imagesc(tsStack(:,:,zvis));colormap('gray');axis image
[rows, columns, numSlices] = size(tsStack);

outputImage = zeros(rows, columns); % Or whatever class you want.
for j= zvis : zvis+intv-1
    
    outputImage=imadd(outputImage,double(tsStack(:,:,j)));
        
end

 
%NUMBER OF ITERATIONS FOR DECONVOLUTION, SET TO BE 5 BUT CAN BE CHANGED
niteration=5;

%PERFORM DECONVOLUTION WITH THE CALCULATED 3D PSF AT A PLANE
Image1proc=deconvhybimg2(outputImage,niteration,outKer(:,:,20));



%OUTPUT FOLDER AND CHANGE filename 
myFolder = 'C:\Users\ahmet\Documents\MATLAB\mathMIBIresults\062730mIdu30mBrduresult';
filename = ['ImSulphurReconst' num2str(i) '.tif'];
R3 = {filename};
charR = cell2mat(R3);
fullFileName = fullfile(myFolder, charR);
imwrite(uint16(Image1proc), fullFileName);


end