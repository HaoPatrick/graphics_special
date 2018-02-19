function [ im_blend ] = mixed_blend( im, mask, im_bg )

[imh, imw, ~] = size(im);
[bgh, bgw, ~] = size(im_bg);

num_source_pixels = imh * imw;
num_bg_pixels = bgh * bgw;
im2var = zeros(bgh, bgw);
im2var(1:num_bg_pixels) = 1:num_bg_pixels;

num_equations = num_bg_pixels - num_source_pixels;
num_equations = num_equations + 4*(num_source_pixels) - (2*bgh + 2*bgw);

v_rgb = {1,2,3};

for c = 1:3
    index_i = [];
    index_j = [];
    value_k = [];
    b = zeros(num_equations, 1);
    
    e = 1;
    for y = 1:bgh
        for x = 1:bgw
            if mask(y,x)==0
                index_i = [index_i e];
                index_j = [index_j im2var(y,x)];
                value_k = [value_k 1];
                b(e) = im_bg(y, x, c);
                e = e + 1;
                continue;
            end
            if y ~= 1
                index_i = [index_i e];
                index_j = [index_j im2var(y,x)];
                value_k = [value_k 1];                
                if mask(y-1, x)
                  index_i = [index_i e];
                  index_j = [index_j im2var(y-1,x)];
                  value_k = [value_k -1];
                end                
                source_grad = im(y,x,c) - im(y-1,x,c);
                target_grad = im_bg(y,x,c) - im_bg(y-1,x,c);                
                if abs(source_grad) > abs(target_grad)
                  b(e) = source_grad;
                else
                  b(e) = target_grad;
                end                
                if mask(y-1,x)==0
                  b(e) = b(e) + im_bg(y-1,x,c);
                end                
                e = e + 1;
            end
            if y ~= bgh
              index_i = [index_i e];
              index_j = [index_j im2var(y,x)];
              value_k = [value_k 1];              
              if mask(y+1, x)
                index_i = [index_i e];
                index_j = [index_j im2var(y+1,x)];
                value_k = [value_k -1];
              end              
              source_grad = im(y,x,c) - im(y+1,x,c);
              target_grad = im_bg(y,x,c) - im_bg(y+1,x,c);              
              if abs(source_grad) >abs(target_grad)
                b(e) = source_grad;
              else
                b(e) = target_grad;
              end               
              if ~mask(y+1,x)
                b(e)=b(e)+im_bg(y+1,x,c);
              end              
              e = e + 1;
            end
            if x ~= bgw
              index_i = [index_i e];
              index_j = [index_j im2var(y,x)];
              value_k = [value_k 1];              
              if mask(y, x+1)
                index_i = [index_i e];
                index_j = [index_j im2var(y,x+1)];
                value_k = [value_k -1];
              end              
              source_grad = im(y,x,c) - im(y,x+1,c);
              target_grad = im_bg(y,x,c) - im_bg(y,x+1,c);              
              if abs(source_grad) > abs(target_grad)
                b(e) = source_grad;
              else
                b(e) = target_grad;
              end              
              if ~mask(y,x+1)
                b(e) = b(e) + im_bg(y,x+1,c);
              end              
              e = e + 1;
            end
            if x ~= 1
              index_i = [index_i e];
              index_j = [index_j im2var(y,x)];
              value_k = [value_k 1];              
              if mask(y, x-1)
                index_i = [index_i e];
                index_j = [index_j im2var(y,x-1)];
                value_k = [value_k -1];
              end              
              source_grad = im(y,x,c) - im(y,x-1,c);
              target_grad = im_bg(y,x,c) - im_bg(y,x-1,c);              
              if abs(source_grad) > abs(target_grad)
                b(e) = source_grad;
              else
                b(e) = target_grad;
              end               
              if ~mask(y,x-1)
                b(e) = b(e) + im_bg(y,x-1,c);
              end              
              e = e + 1;
            end
        end
    end    
    A = sparse(index_i, index_j, value_k, num_equations, num_bg_pixels);
    v_rgb{c} = A\b;
end
for c = 1:3
  im_blend(:,:,c) = reshape(v_rgb{c}, [bgh bgw]);
end
end