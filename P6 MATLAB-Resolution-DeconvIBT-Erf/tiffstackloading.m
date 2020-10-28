function out = tiffstackloading(fname)


%fname = 'C:\Users\ahmet\Documents\MATLAB\mathMIBIdata\04082019deconv\SUM_mbrducell1x-2.tif';

tiff_info = imfinfo(fname); % return tiff structure, one element per image
tiff_stack = imread(fname, 1) ; % read in first image
%concatenate each successive tiff to tiff_stack
for ii = 2 : size(tiff_info, 1)
    temp_tiff = imread(fname, ii);
    tiff_stack = cat(3 , tiff_stack, temp_tiff);
end

out=tiff_stack;

end