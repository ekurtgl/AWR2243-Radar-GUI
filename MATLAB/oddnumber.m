function y = oddnumber(x)

% get a nearest odd number of x

[nx] = length(x);
y = zeros(1,nx);
for k=1:nx  
  y(k) = floor(x(k));
  if rem(y(k),2)==0,
   y(k)=ceil(x(k));
  end
  if rem(y(k),2)==0,
   y(k)=y(k)+1;
  end
end