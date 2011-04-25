require 'yaml'
$LOAD_PATH.unshift "/var/lib/gems/1.8/gems/kramdown-0.13.2/lib"
$LOAD_PATH.unshift "/var/lib/gems/1.8/gems/mustache-0.99.3/lib/"
require 'kramdown'
require 'mustache'

config = {
  'input_enc' => 'utf-8',
  'input_ext' => '.mkd',
  'input_dir' => 'pages',
  'output_enc' => 'utf-8',
  'output_ext' => '.html',
  'output_dir' => 'output',
  'template' => 'templates/template.mustache',
  'assets' => 'media'
}

begin
  config.merge YAML::load File.open 'site.yaml'
rescue; end

SRC_ASSETS = FileList[
  File.join(config['assets'], '**', '*')].
    find_all {|f| FileTest.file?(f)}
SRC_PAGES = FileList[
  File.join(config['input_dir'], '**', '*' + config['input_ext'])]

OUT_ASSETS = SRC_ASSETS.collect do |s|
  s.sub config['assets'], config['output_dir']; end
OUT_PAGES = SRC_PAGES.collect do |s|
  s.sub(config['input_dir'], config['output_dir']).
    ext config['output_ext']; end

task :default => :gen

desc 'generate the site'
task :gen => OUT_PAGES + OUT_ASSETS do
end

SRC_PAGES.zip(OUT_PAGES).each do |src, out|
  file out => [src, config['template']] do |t|
    make_page t.name, *t.prerequisites
    puts "generated #{t.name}"
  end
end

SRC_ASSETS.zip(OUT_ASSETS).each do |src, out|
  file out => [src] do |t|
    mkpath File.dirname(t.name), :verbose => false
    cp t.prerequisites[0], t.name
  end
end

def make_page out, src, template
  text = IO.read src
  context = {
    :content => Kramdown::Document.new(text).to_html}
  page = Mustache.render IO.read(template), context
  File.open(out, 'w') {|f| f.write page}
end
