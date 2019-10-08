"""Test harness for Image Sequence References."""

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils

import unittest


class ImageSequenceReferenceTests(
    unittest.TestCase, otio_test_utils.OTIOAssertions
):
    def test_create(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            image_number_zero_padding=5,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(60, 30),
            ),
            value_step=3,
            frame_duration=otio.opentime.RationalTime(1, 30),
            metadata={"custom": {"foo": "bar"}},
        )

        # Check Values
        self.assertEqual(ref.target_url_base, "file:///show/seq/shot/rndr/")
        self.assertEqual(ref.name_prefix, "show_shot.")
        self.assertEqual(ref.name_suffix, ".exr")
        self.assertEqual(ref.image_number_zero_padding, 5)
        self.assertEqual(
            ref.available_range,
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(60, 30),
            )
        )
        self.assertEqual(ref.value_step, 3)
        self.assertEqual(ref.frame_duration, otio.opentime.RationalTime(1, 30))
        self.assertEqual(ref.metadata, {"custom": {"foo": "bar"}})

    def test_str(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            start_value=1,
            value_step=3,
            frame_duration=otio.opentime.RationalTime(1, 30),
            image_number_zero_padding=5,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(60, 30),
            ),
            metadata={"custom": {"foo": "bar"}},
        )
        self.assertEqual(
            str(ref),
            'ImageSequenceReference('
            '"file:///show/seq/shot/rndr/", '
            '"show_shot.", '
            '".exr", '
            '1, '
            '3, '
            'RationalTime(1, 30), '
            '5, '
            'TimeRange(RationalTime(0, 30), RationalTime(60, 30)), '
            "{'custom': {'foo': 'bar'}}"
            ')'
        )

    def test_repr(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            start_value=1,
            value_step=3,
            frame_duration=otio.opentime.RationalTime(1, 30),
            image_number_zero_padding=5,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(60, 30),
            ),
            metadata={"custom": {"foo": "bar"}},
        )
        ref_value = (
            'ImageSequenceReference('
            "target_url_base='file:///show/seq/shot/rndr/', "
            "name_prefix='show_shot.', "
            "name_suffix='.exr', "
            'start_value=1, '
            'value_step=3, '
            'frame_duration={}, '
            'image_number_zero_padding=5, '
            'available_range={}, '
            "metadata={{'custom': {{'foo': 'bar'}}}}"
            ')'.format(repr(ref.frame_duration), repr(ref.available_range))
        )
        self.assertEqual(repr(ref), ref_value)

    def test_serialize_roundtrip(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            image_number_zero_padding=5,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(60, 30),
            ),
            value_step=3,
            frame_duration=otio.opentime.RationalTime(1, 30),
            metadata={"custom": {"foo": "bar"}},
        )

        encoded = otio.adapters.otio_json.write_to_string(ref)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(ref, decoded)

        encoded2 = otio.adapters.otio_json.write_to_string(decoded)
        self.assertEqual(encoded, encoded2)

        # Check Values
        self.assertEqual(
            decoded.target_url_base, "file:///show/seq/shot/rndr/"
        )
        self.assertEqual(decoded.name_prefix, "show_shot.")
        self.assertEqual(decoded.name_suffix, ".exr")
        self.assertEqual(decoded.image_number_zero_padding, 5)
        self.assertEqual(
            decoded.available_range,
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(60, 30),
            )
        )
        self.assertEqual(decoded.value_step, 3)
        self.assertEqual(
            decoded.frame_duration, otio.opentime.RationalTime(1, 30)
        )
        self.assertEqual(decoded.metadata, {"custom": {"foo": "bar"}})

    def test_number_of_images_in_sequence(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 24),
                otio.opentime.RationalTime(48, 24),
            ),
            frame_duration=otio.opentime.RationalTime(1, 24),
        )

        self.assertEqual(ref.number_of_images_in_sequence(), 48)

    def test_number_of_images_in_sequence_with_skip(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 24),
                otio.opentime.RationalTime(48, 24),
            ),
            value_step=2,
            frame_duration=otio.opentime.RationalTime(1, 12),
        )

        self.assertEqual(ref.number_of_images_in_sequence(), 24)

        ref.value_step = 3
        ref.frame_duration = otio.opentime.RationalTime(3, 24)
        self.assertEqual(ref.number_of_images_in_sequence(), 16)

    def test_image_url_for_image_number(self):
        all_images_urls = [
            "file:///show/seq/shot/rndr/show_shot.{:04}.exr".format(i)
            for i in range(1, 49)
        ]
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            image_number_zero_padding=4,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 24),
                otio.opentime.RationalTime(48, 24),
            ),
            start_value=1,
            value_step=1,
            frame_duration=otio.opentime.RationalTime(1, 24),
        )

        generated_urls = [
            ref.image_url_for_image_number(i)
            for i in range(ref.number_of_images_in_sequence())
        ]
        self.assertEqual(all_images_urls, generated_urls)

    def test_image_url_for_image_number_steps(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            image_number_zero_padding=4,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 24),
                otio.opentime.RationalTime(48, 24),
            ),
            start_value=1,
            value_step=2,
            frame_duration=otio.opentime.RationalTime(2, 24),
        )

        all_images_urls = [
            "file:///show/seq/shot/rndr/show_shot.{:04}.exr".format(i)
            for i in range(1, 49, 2)
        ]
        generated_urls = [
            ref.image_url_for_image_number(i)
            for i in range(ref.number_of_images_in_sequence())
        ]
        self.assertEqual(all_images_urls, generated_urls)

        ref.value_step = 3
        ref.frame_duration = otio.opentime.RationalTime(3, 24)
        all_images_urls_threes = [
            "file:///show/seq/shot/rndr/show_shot.{:04}.exr".format(i)
            for i in range(1, 49, 3)
        ]
        generated_urls_threes = [
            ref.image_url_for_image_number(i)
            for i in range(ref.number_of_images_in_sequence())
        ]
        self.assertEqual(all_images_urls_threes, generated_urls_threes)

        ref.value_step = 2
        ref.frame_duration = otio.opentime.RationalTime(2, 24)
        ref.start_value = 0
        all_images_urls_zero_first = [
            "file:///show/seq/shot/rndr/show_shot.{:04}.exr".format(i)
            for i in range(0, 48, 2)
        ]
        generated_urls_zero_first = [
            ref.image_url_for_image_number(i)
            for i in range(ref.number_of_images_in_sequence())
        ]
        self.assertEqual(all_images_urls_zero_first, generated_urls_zero_first)
