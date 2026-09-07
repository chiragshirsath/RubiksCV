import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
import numpy as np
from PIL import Image
import random
import os

# Base colors (R, G, B) mapping
COLORS = {
    0: (255, 255, 255), # White
    1: (255, 213, 0),   # Yellow
    2: (183, 18, 52),   # Red
    3: (255, 88, 0),    # Orange
    4: (0, 155, 72),    # Green
    5: (0, 70, 173)     # Blue
}

class SyntheticRubiksDataset(Dataset):
    def __init__(self, num_samples, transform=None):
        self.num_samples = num_samples
        self.transform = transform
        self.data = []
        self.labels = []
        
        self.generate_data()

    def apply_gradient_shadow(self, img_array):
        # Apply a random gradient to simulate shadows
        h, w, _ = img_array.shape
        x = np.linspace(random.uniform(0.3, 1.0), random.uniform(0.3, 1.0), w)
        y = np.linspace(random.uniform(0.3, 1.0), random.uniform(0.3, 1.0), h)
        xv, yv = np.meshgrid(x, y)
        gradient = (xv * yv)[..., np.newaxis]
        return np.clip(img_array * gradient, 0, 255).astype(np.uint8)

    def generate_data(self):
        for _ in range(self.num_samples):
            label = random.randint(0, 5)
            base_color = COLORS[label]
            
            # Create base 32x32 image
            img_array = np.full((32, 32, 3), base_color, dtype=np.float32)
            
            # Add random uniform noise
            noise = np.random.normal(0, 15, (32, 32, 3))
            img_array = np.clip(img_array + noise, 0, 255)
            
            # Apply gradient shadow
            if random.random() > 0.3:
                img_array = self.apply_gradient_shadow(img_array)
                
            img = Image.fromarray(img_array.astype(np.uint8))
            self.data.append(img)
            self.labels.append(label)

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        img = self.data[idx]
        label = self.labels[idx]
        
        if self.transform:
            img = self.transform(img)
            
        return img, label

class StickerNet(nn.Module):
    def __init__(self):
        super(StickerNet, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(16)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(32)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(32 * 8 * 8, 128)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(128, 6)

    def forward(self, x):
        x = self.pool(torch.relu(self.bn1(self.conv1(x)))) # 32x32 -> 16x16
        x = self.pool(torch.relu(self.bn2(self.conv2(x)))) # 16x16 -> 8x8
        x = x.view(x.size(0), -1)
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

def train():
    print("Generating synthetic dataset...")
    # Heavy color jitter to simulate terrible webcams and white-balance issues
    transform = transforms.Compose([
        transforms.ColorJitter(brightness=0.5, contrast=0.5, saturation=0.5, hue=0.1),
        transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0)),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    
    train_dataset = SyntheticRubiksDataset(20000, transform=transform)
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Training on device: {device}")
    
    model = StickerNet().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    epochs = 5
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for i, (inputs, labels) in enumerate(train_loader):
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
        print(f"Epoch {epoch+1}/{epochs}, Loss: {running_loss/len(train_loader):.4f}, Accuracy: {100 * correct / total:.2f}%")
        
    print("Training complete. Saving model...")
    torch.save(model.state_dict(), "sticker_net.pth")
    print("Model saved to sticker_net.pth")

if __name__ == "__main__":
    train()
