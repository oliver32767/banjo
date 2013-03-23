<div id="blog-title"><a href="/">{{title}}</a></div>
<div id="navcontainer">

%if len(topic.locator) > 0:
  <ul id="nav">
    %for parent in breadcrumb:
      <li><a href="{{parent.locator}}">{{parent.meta['title']}}</a></li>
      <li><span>></span></li>
    %end
  </ul>
%end
%if len(subtopics) > 0:
  <ul id="nav">
    %i = 0
    %for subtopic in subtopics:
      <li><a href="{{subtopic.locator}}">{{subtopic.meta['title']}}</a></li>
      %i+=1
      %if i < len(subtopics):
        <li><span>&bull;</span></li>
      %end
    %end
  </ul>
%end
</div>