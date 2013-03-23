<!DOCTYPE html>
<html>
<head>
  <title>{{title}}: {{post.meta['title']}}</title>
  <link href="/static/styles/{{style}}" media="screen" rel="stylesheet" type="text/css" />
  <link href="/static/styles/{{pygment_style}}" media="screen" rel="stylesheet" type="text/css" />
</head>
<body>

<div id="body-wrapper">

%include includes/navigation.tpl title=title, topic=topic, subtopics=subtopics, breadcrumb=breadcrumb

<div class="post">
  <div class="post-title">{{post.meta['title']}}</div>
  <div class="post-date">{{post.date.strftime('%B %d, %Y')}}</div>
  <div class="post-author">{{post.meta['author']}}</div>
  <div class="post-body">{{!post.contents}}</div>
</div>

%import urllib
%if len(post.meta['tags']) > 0:
  <div id="post-tags">
    <ul id="post-tag">
    %for tag in post.meta['tags']:
      %urltag=urllib.quote_plus(tag)
      <li>#<a href="/?tag={{urltag}}">{{tag}}</a></li>
    %end
    </ul>
  </div>
%end

% if disqus_shortname:
<div id="disqus_thread"></div>
<script type="text/javascript">
    var disqus_shortname = '{{disqus_shortname}}';
    var disqus_developer = 1;
    (function() {
        var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
        dsq.src = 'http://' + disqus_shortname + '.disqus.com/embed.js';
        (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
    })();
</script>
<noscript>Please enable JavaScript to view the <a href="http://disqus.com/?ref_noscript">comments powered by Disqus.</a></noscript>
% end

<div id="powered-by">
  <small>powered by <a href="https://github.com/oliver32767/banjo">banjo</a>.</small>
</div>

</div>

</body>
</html>
