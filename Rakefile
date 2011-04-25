require "yaml"

config = {
  "input_enc" => "utf-8",
  "input_ext" => ".mkd",
  "input_dir" => "pages",
  "output_enc" => "utf-8",
  "output_ext" => ".html",
  "output_dir" => "output",
  "template" => "templates/template.mustache",
  "assets" => "media"
}

begin
  config.merge YAML::load File.open "config.yaml"
rescue; end

task :default => :gen

desc "generate the site"
multitask :gen => [:pages, :assets] do
  puts "generate code"
end

file :pages
FileList["#{:input_dir}/*.#{:input_ext}"].each do |src|
  file :pages => src
end

file :assets
FileList["#{:asset_dir}/*"].each do |src|
  file :assets => src
end

desc "blupp"
task :compile => :codeGen do
  #do the compilation
  puts "compile"
end

desc "bli"
task :dataLoad => :codeGen do
  # load the test data
  puts "load data"
end

desc "bla"
task :test => [:compile, :dataLoad] do
  puts "test"
end
