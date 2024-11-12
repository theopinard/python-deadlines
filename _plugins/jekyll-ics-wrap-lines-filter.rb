module Jekyll
  module WrapLinesFilter
    def wrap_lines(input_string)
      max_length = 72
      wrapped_string = ""

      while input_string.length > max_length
        line = input_string.slice!(0, max_length)
        line += "\r\n "
        wrapped_string += line
      end

      wrapped_string += input_string

      wrapped_string

    end
  end
end

Liquid::Template.register_filter(Jekyll::WrapLinesFilter)
