<!DOCTYPE html>
<html>
<head>
  <title>{{title}}</title>
  <link href="/static/styles/{{style}}" media="screen" rel="stylesheet" type="text/css" />
  <link href="/static/styles/{{pygment_style}}" media="screen" rel="stylesheet" type="text/css" />
</head>
<body>
<div id="body-wrapper">

%include includes/navigation.tpl title=title, topic=topic, subtopics=subtopics, breadcrumb=breadcrumb

<div class="content">
  {{!topic.contents}}
</div>

%import urllib
%if len(tags) > 0:
  <div id="post-tags">
    <ul id="post-tag">
      <li>all posts tagged</li>
    %for tag in tags:
      %urltag=urllib.quote_plus(tag)
      <li>#<a href="/?tag={{urltag}}">{{tag}}</a></li>
    %end
    </ul>
  </div>
%end
  
% for post in posts:
  <div class="post">
    <div class="post-title">
      % if topic.locator == '/':
        <a href="{{!post.locator}}">{{post.meta['title']}}</a>
      % else:
        <a href="{{!topic.locator + post.locator}}">{{post.meta['title']}}</a>
      % end
    </div>
    <div class="post-date">{{post.date.strftime('%B %d, %Y')}}</div>
    <div class="post-author">{{post.meta['author']}}</div>
    <div class="post-summary">
      {{!post.summary}}
      <div class="post-more-link">
        % if topic.locator == '/':
        <a href="{{!post.locator}}">...more</a>
      % else:
        <a href="{{!topic.locator + post.locator}}">...more</a>
      % end
      </div>
    </div>
  </div>
% end

% if has_prev or has_next:
<div id="page-navigation">
  {{!'<a href="/'+(str(page-1))+'">Previous</a>' if has_prev else 'Previous'}} | 
  {{!'<a href="/'+(str(page+1))+'">Next</a>' if has_next else 'Next'}}
</div>
%end

<div id="powered-by">
  <small>powered by <a href="https://github.com/oliver32767/banjo">banjo</a>.</small>
</div>

</div>
</body>
</html>
