import numpy as np

asd = np.random.rand(2,2)

print("".join(str(asd)))

coefs = np.polyfit(asd[:,0],asd[:,1],1)
print("".join(str(coefs)))