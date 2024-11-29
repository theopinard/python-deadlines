# _plugins/timezone_filters.rb
require 'tzinfo'

module Jekyll
  module TimezoneFilters
    def to_utc(date, timezone = "Etc/GMT+12")
      return nil if date.nil? || date == "TBA" || date == "None" || date == "Cancelled"

      date = Time.parse(date.to_s) unless date.is_a?(Time)

      begin
        if timezone&.start_with?("UTC")
          offset = timezone[3..-1].to_i
          offset_seconds = offset * 3600
          time_with_offset = Time.at(date.to_i - offset_seconds).utc
          time_with_offset.strftime("%Y%m%dT%H%M%SZ")
        else
          tz = TZInfo::Timezone.get(timezone)
          local = tz.local_datetime(date.year, date.month, date.day, date.hour, date.min, date.sec)
          utc = tz.local_to_utc(local)
          utc.strftime("%Y%m%dT%H%M%SZ")
        end
      rescue TZInfo::InvalidTimezoneIdentifier
        tz = TZInfo::Timezone.get("Etc/GMT+12")
        local = tz.local_datetime(date.year, date.month, date.day, date.hour, date.min, date.sec)
        utc = tz.local_to_utc(local)
        utc.strftime("%Y%m%dT%H%M%SZ")
      end
    end
  end
end

Liquid::Template.register_filter(Jekyll::TimezoneFilters)
