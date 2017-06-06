from shapeworld import CaptionerMixer
from shapeworld.dataset import CaptionAgreementDataset
from shapeworld.generators import GenericGenerator
from shapeworld.captioners import ExistentialCaptioner, SpatialCaptioner, QuantificationCaptioner, ConjunctionCaptioner, DisjunctionCaptioner


class CombinationDataset(CaptionAgreementDataset):

    def __init__(self, entity_counts, train_entity_counts, validation_entity_counts, test_entity_counts, shapes_range, colors_range, textures_range, caption_size, words, distribution=None, train_distribution=None, validation_distribution=None, test_distribution=None, correct_ratio=None, train_correct_ratio=None, validation_correct_ratio=None, test_correct_ratio=None, realizer=None, world_size=None, world_color=None, shapes=None, colors=None, textures=None, rotation=None, size_range=None, distortion_range=None, shade_range=None, noise_range=None, collision_tolerance=None, boundary_tolerance=None, quantifier_tolerance=None, **kwargs):
        world_generator = GenericGenerator(entity_counts, world_size, world_color, shapes, colors, textures, rotation, size_range, distortion_range, shade_range, noise_range, collision_tolerance, boundary_tolerance, train_entity_counts=train_entity_counts, validation_entity_counts=validation_entity_counts, test_entity_counts=test_entity_counts, shapes_range=shapes_range, colors_range=colors_range, textures_range=textures_range)
        captioners = [ExistentialCaptioner(world_generator.shapes, world_generator.colors, world_generator.textures, quantifier_tolerance=quantifier_tolerance), SpatialCaptioner(world_generator.shapes, world_generator.colors, world_generator.textures, quantifier_tolerance=quantifier_tolerance), QuantificationCaptioner(world_generator.shapes, world_generator.colors, world_generator.textures, quantifier_tolerance=quantifier_tolerance)]
        captioners = [ConjunctionCaptioner(captioners=captioners, quantifier_tolerance=quantifier_tolerance), DisjunctionCaptioner(captioners=captioners, quantifier_tolerance=quantifier_tolerance)]
        world_captioner = CaptionerMixer(captioners=captioners, distribution=distribution, train_distribution=train_distribution, validation_distribution=validation_distribution, test_distribution=test_distribution)
        super(CombinationDataset, self).__init__(
            world_generator=world_generator,
            world_captioner=world_captioner,
            caption_size=caption_size,
            words=words,
            incorrect_world_ratio=0.0,
            correct_ratio=correct_ratio,
            train_correct_ratio=correct_ratio,
            validation_correct_ratio=validation_correct_ratio,
            test_correct_ratio=test_correct_ratio,
            caption_realizer=realizer)


dataset = CombinationDataset
CombinationDataset.dataset_name = 'combination'
CombinationDataset.default_config = {
    'entity_counts': [1, 2, 3, 4, 5, 6, 7, 8],
    'train_entity_counts': [1, 2, 3, 4, 5, 7],
    'validation_entity_counts': [6],
    'test_entity_counts': [8],
    'shapes_range': [2, 4],
    'colors_range': [2, 4],
    'textures_range': [1, 1],
    'caption_size': 25,
    'words': [',', '.', 'a', 'above', 'all', 'an', 'and', 'are', 'below', 'black', 'blue', 'circle', 'circles', 'cross', 'crosses', 'cyan', 'either', 'ellipse', 'ellipses', 'every', 'green', 'is', 'left', 'magenta', 'most', 'no', 'of', 'or', 'pentagon', 'pentagons', 'rectangle', 'rectangles', 'red', 'right', 'semicircle', 'semicircles', 'shape', 'shapes', 'some', 'square', 'squares', 'the', 'there', 'to', 'triangle', 'triangles', 'two', 'white', 'yellow']
}
