import timm
import torch.nn as nn

class CustomModel(nn.Module):
    def __init__(self, base_model="hf_hub:timm/vit_small_patch16_224.augreg_in21k_ft_in1k", num_classes=4):
        super(CustomModel, self).__init__()
        # Load the pre-trained model
        self.base_model = timm.create_model(base_model, pretrained=True)
        # Replace the head with your own classifier
        in_features = self.base_model.head.out_features  # Get the output features of the original head
        # self.base_model.head = nn.Identity()  # Remove the pre-trained head
        
        # Add custom layers
        self.classifier = nn.Sequential(
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(in_features, num_classes)  # Final layer with `num_classes` output
        )

    def forward(self, x):
        x = self.base_model(x)  # Forward through the base model
        x = self.classifier(x)  # Forward through the custom classifier
        return x