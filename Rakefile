require 'rake/clean'
require 'yaml'
require 'rubygems'
require 'kramdown'
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

CLEAN.include '.menu.yaml'
CLOBBER.include OUT_ASSETS + OUT_PAGES

task :default => :gen

desc 'generate the site'
task :gen => OUT_PAGES + OUT_ASSETS + ['Rakefile'] do
end

file '.menu.yaml' => ['site.yaml'] + SRC_PAGES do |t|
  $menu = []
  config['menu'].each do |p|
    src = File.join config['input_dir'], p + config['input_ext']
    meta, _ = parse_file src
    out = src.sub(config['input_dir'] + '/', '').ext config['output_ext']
    $menu << {
      'title' => meta['Title'] || meta['title'],
      'url' => out}
  end
  File.open('.menu.yaml', 'w').write YAML.dump $menu
end

def dir_exists! f
    mkpath File.dirname(f), :verbose => false
end

SRC_PAGES.zip(OUT_PAGES).each do |src, out|
  file out => [src, config['template'], '.menu.yaml'] do |t|
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

def parse_file src
  content = IO.read src
  pieces = content.split(/^(-{3})/).compact
  if pieces.size < 3
    raise RuntimeError.new(
      "The file '#{filename}' does not seem to have a metadata section.")
  end

  meta = YAML.load(pieces[2]) || {}
  content = pieces[4..-1].join.strip
  [meta, content]
end

def make_page out, src, template
  meta, content = parse_file src
  context = {
    :content => Kramdown::Document.new(content).to_html,
    :title => meta['Title'] || meta['title'],
    :menu => $menu }
  page = Mustache.render IO.read(template), context
  File.open(out, 'w') {|f| f.write page}
end

