import numpy
import torch

print(numpy.__version__)

a = torch.cuda.current_device()
print("CURRENT DEVICE: ", a)
print(torch.cuda.get_device_name(a))


