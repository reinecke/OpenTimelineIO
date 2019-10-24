#include "opentimelineio/imageSequenceReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {

ImageSequenceReference::ImageSequenceReference(std::string const& target_url_base,
                      std::string const& name_prefix,
                      std::string const& name_suffix,
                      int start_value,
                      int value_step,
                      double const rate,
                      int image_number_zero_padding,
                      MissingFramePolicy const missing_frame_policy,
                      optional<TimeRange> const& available_range,
                      AnyDictionary const& metadata)
    : Parent(std::string(), available_range, metadata),
    _target_url_base(target_url_base),
    _name_prefix(name_prefix),
    _name_suffix(name_suffix),
    _start_value {start_value},
    _value_step {value_step},
    _rate {rate},
    _image_number_zero_padding {image_number_zero_padding},
    _missing_frame_policy {missing_frame_policy} {
    }

    ImageSequenceReference::~ImageSequenceReference() {
    }

    RationalTime
    ImageSequenceReference::frame_duration() const {
        return RationalTime((double)_value_step, _rate);
    }

    int ImageSequenceReference::number_of_images_in_sequence() const {
        if (!this->available_range().has_value()) {
            return 0;
        }
        
        double playback_rate = (_rate / (double)_value_step);
        int num_frames = this->available_range().value().duration().to_frames(playback_rate);
        return num_frames;
    } 

    std::string
    ImageSequenceReference::target_url_for_image_number(int const image_number, ErrorStatus* error_status) const {
        if (image_number >= this->number_of_images_in_sequence()) {
            *error_status = ErrorStatus(ErrorStatus::ILLEGAL_INDEX);
            return std::string();
        }
        const int file_image_num = _start_value + (image_number * _value_step);
        const bool is_negative = (file_image_num < 0);
        std::string image_num_string = std::to_string(abs(file_image_num));
        std::string zero_pad = std::string();
        if (image_num_string.length() <  _image_number_zero_padding) {
            zero_pad = std::string(_image_number_zero_padding - image_num_string.length(), '0');
        }

        std::string sign = std::string();
        if (is_negative) {
            sign = "-";
        }

        std::string out_string = _target_url_base + _name_prefix + sign + zero_pad + image_num_string + _name_suffix;
        *error_status = ErrorStatus(ErrorStatus::OK);
        return out_string;
    }

    RationalTime
    ImageSequenceReference::presentation_time_for_image_number(int const image_number, ErrorStatus* error_status) const {
        if (image_number >= this->number_of_images_in_sequence()) {
            *error_status = ErrorStatus(ErrorStatus::ILLEGAL_INDEX);
            return RationalTime();
        }

        auto first_frame_time = this->available_range().value().start_time();
        auto time_multiplier = TimeTransform(first_frame_time, image_number, -1);
        return time_multiplier.applied_to(frame_duration());
    }

    bool ImageSequenceReference::read_from(Reader& reader) {
        auto result = reader.read("target_url_base", &_target_url_base) &&
                reader.read("name_prefix", &_name_prefix) &&
                reader.read("name_suffix", &_name_suffix) &&
                reader.read("start_value", &_start_value) &&
                reader.read("value_step", &_value_step) &&
                reader.read("rate", &_rate) &&
                reader.read("image_number_zero_padding", &_image_number_zero_padding);

                std::string missing_frame_policy_value;
                result && reader.read("missing_frame_policy", &missing_frame_policy_value);
                if (!result) {
                    return result;
                } 

                if (missing_frame_policy_value == "error") {
                    _missing_frame_policy = MissingFramePolicy::error;
                }
                else if (missing_frame_policy_value == "black") {
                    _missing_frame_policy = MissingFramePolicy::black;
                }
                else if (missing_frame_policy_value == "hold") {
                    _missing_frame_policy = MissingFramePolicy::hold;
                }
                else {
                    // TODO: This fails silently, what should we do?
                }

                return result && Parent::read_from(reader);
    }

    void ImageSequenceReference::write_to(Writer& writer) const {
        Parent::write_to(writer);
        writer.write("target_url_base", _target_url_base);
        writer.write("name_prefix", _name_prefix);
        writer.write("name_suffix", _name_suffix);
        writer.write("start_value", _start_value);
        writer.write("value_step", _value_step);
        writer.write("rate", _rate);
        writer.write("image_number_zero_padding", _image_number_zero_padding);

        std::string missing_frame_policy_value;
        switch (_missing_frame_policy)
        {
        case MissingFramePolicy::error:
            missing_frame_policy_value = "error";
            break;
        case MissingFramePolicy::black:
            missing_frame_policy_value = "black";
            break;
        case MissingFramePolicy::hold:
            missing_frame_policy_value = "hold";
            break;
        }
        writer.write("missing_frame_policy", missing_frame_policy_value);
    }
} }