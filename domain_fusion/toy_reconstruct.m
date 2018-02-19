function [ im_out ] = toy_reconstruct( im )

[imh,imw,~] = size(im);
im2var = zeros(imh, imw);
num_pixels=imh*imw;
im2var(1:num_pixels) = 1:num_pixels; 

num_equations = 2*num_pixels + 1;
A = sparse([],[],[],num_equations, num_pixels,num_pixels*2);
b = zeros(num_equations, 1);

e = 1;
for y = 1:imh
    for x = 1:imw
        if x~=imw
            A(e, im2var(y,x+1)) = 1;
            A(e, im2var(y,x)) = -1;
            b(e) = im(y,x+1)-im(y,x);  
            e = e+1;
        end
        if y~=imh
            A(e, im2var(y+1,x)) = 1;
            A(e, im2var(y,x)) = -1;
            b(e) = im(y+1,x)-im(y,x);  
            e = e+1;
        end
    end  
end

A(e, im2var(1,1)) = 1;
b(e) = im(1,1);

v = A\b;
im_out = reshape(v, [imh imw]);
imshow(im_out);

end