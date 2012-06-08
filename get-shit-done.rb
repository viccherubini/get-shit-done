#!/usr/bin/env ruby

HOSTS_FILE = "/etc/hosts"
USER_SITES_FILE = "~/.get-shit-done.ini"
GLOBAL_SITES_FILE = "./sites.ini"
START_TOKEN = "## start-gsd"
END_TOKEN = "## end-gsd"

def get_sites(filename)
  sites = []
  path = File.expand_path(filename)
  if File.exists?(path)
    File.read(path).scan(/^sites\s*=\s*(.*)/).flatten.each do |m|
      sites += m.split(",").map(&:strip)
    end
  end
  sites
end

def flush_dns
  cmd = case RUBY_PLATFORM
    when /linux/
      ["/etc/init.d/networking", "restart"]
    when /darwin/
      ["dscacheutil", "-flushcache"]
    else
      ["echo", "Please contribute DNS cache flush command on GitHub."]
  end
  system(*cmd)
end

def work?
  File.read(HOSTS_FILE).include?(START_TOKEN)
end

def work
  abort "error: work mode already set" if work?

  sites = get_sites(GLOBAL_SITES_FILE) + get_sites(USER_SITES_FILE)
  abort "error: no sites configured" if sites.empty?

  File.open(HOSTS_FILE, "a") do |f|
    f.puts START_TOKEN
    sites.uniq.sort.each do |site|
      f.puts "127.0.0.1\t#{site}"
      f.puts "127.0.0.1\twww.#{site}"
    end
    f.puts END_TOKEN
  end

  flush_dns
end

def play?
  !work?
end

def play
  abort "error: play mode already set" if play?

  File.open(HOSTS_FILE, "r+") do |f|
    i = f.read.index(/#{START_TOKEN}.*#{END_TOKEN}/m)
    f.truncate(i) unless i.nil?
  end

  flush_dns
end

mode = ARGV.first
case mode
when "work", "play"
  Object.send(mode)
else
  abort "usage: #{File.basename($PROGRAM_NAME)} <work | play>"
end
