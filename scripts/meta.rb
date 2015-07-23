#/usr/bin/ruby
require "geo_combine"
require "fileutils"
require "byebug"
require "json"

xmls = Dir[File.join("..", "mn-geospatial-commons", "*.xml")]
xmls.each do |x|
    puts x
    filename = x.split("/")[-1]
    dir_sub = filename.sub(".xml", "")
    dir = File.join("..", "mn-geospatial-commons", dir_sub)
    if not Dir.exist?(dir)
        Dir.mkdir(dir)
    end

    FileUtils.cp(x, File.join(dir, "fgdc.xml"))
    metadata = GeoCombine::Fgdc.new(x)
    File.write(File.join(dir,"geoblacklight.json"), metadata.to_geoblacklight.to_json)

end
