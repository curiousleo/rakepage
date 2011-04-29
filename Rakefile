require 'rake/clean'
require 'yaml'
require 'rubygems'
require 'tilt'
require 'mustache'

config = {
  'input_enc' => 'utf-8', 'input_ext' => '.mkd', 'input_dir' => 'pages',
  'output_enc' => 'utf-8', 'output_ext' => '.html', 'output_dir' => 'output',
  'template' => 'templates/template.mustache', 'assets' => 'media'
}

config.merge! YAML.load File.open 'site.yaml'

$menu = nil

SRC_ASSETS = FileList[
  File.join config['assets'], '**', '*'].
    find_all {|f| FileTest.file? f}
SRC_PAGES = FileList[
  File.join config['input_dir'], '**', '*' + config['input_ext']]

OUT_ASSETS = SRC_ASSETS.collect do |s|
  s.sub config['assets'], config['output_dir']; end
OUT_PAGES = SRC_PAGES.collect do |s|
  s.sub(config['input_dir'], config['output_dir']).
    ext config['output_ext']; end

CLOBBER.include OUT_ASSETS + OUT_PAGES

task :default => :gen

desc 'generate the site'
task :gen => OUT_PAGES + OUT_ASSETS + ['Rakefile'] do
  puts 'Site generated.'
end

def dir_exists! f
    mkpath File.dirname(f), :verbose => false
end

SRC_PAGES.zip(OUT_PAGES).each do |src, out|
  file out => [src, config['template']] do |t|
    out, src, template = t.name, *t.prerequisites
    dir_exists! out
    make_page out, src, template
  end
end

SRC_ASSETS.zip(OUT_ASSETS).each do |src, out|
  file out => [src, 'site.yaml'] do |t|
    dir_exists! t.name
    cp t.prerequisites[0], t.name, :verbose => false
  end
end

def make_page out, src, template
  context = {
    :content => Tilt.new(src).render,
    :menu => $menu }
  page = Mustache.render IO.read(template), context
  File.open(out, 'w') {|f| f.write page}
end

task :auto do |t|
  require 'watchr'

  src_pages = File.join config['input_dir'], '**', '*' + config['input_ext']
  src_assets = File.join config['assets'], '**', '*'

  script = Watchr::Script.new
  script.watch("[#{src_pages}]|[#{src_assets}]") do |file|
    system("date +%T && rake -s"); end
  controller = Watchr::Controller.new(script, Watchr.handler.new)

  puts 'Started automatic site generation.'
  controller.run
end
