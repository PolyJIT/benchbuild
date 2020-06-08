
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css" integrity="sha384-PsH8R72JQ3SOdhVi3uxftmaW6Vc51MKb0q5P2rRUpPvrszuE4W1povHYgTpBfshb" crossorigin="anonymous">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.12.0/styles/default.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.12.0/highlight.min.js"></script>
    <script>hljs.initHighlightingOnLoad();</script>
    <title>IJPP Code Report</title>
  </head>

  <body>
    <div class="container-fluid">
{% for row in data %}
      <h3> {{ row[0] }} :: {{ row[1] }} </h3>
      <h4> {{ row[2].name }} :: {{ row[2].fn_hash }} </h4>
      <p>  AST </p>
      <div class="row">
        <div class="col-md-6">
            <pre><code class="C++">{{ row[3] }}</code></pre>
        </div>
        <div class="col-md-6">
            <pre><code class="C++">{{ row[6] }}</code></pre>
        </div>
      </div>
      <p>  Schedule Tree </p>
      <div class="row">
        <div class="col-md-6">
            <pre><code class="JSON">{{ row[4] }}</code></pre>
        </div>
        <div class="col-md-6">
            <pre><code class="JSON">{{ row[7] }}</code></pre>
        </div>
      </div>
      <p>  Diagnostic (Limit 240 Chars each)</p>
      <div class="row">
        <div class="col-md-6">
            <pre>{{ row[5] }}</pre>
        </div>
        <div class="col-md-6">
            <pre>{{ row[8] }}</pre>
        </div>
      </div>
      <hr/>
{% endfor %}
    </div> <!-- /container -->
  </body>
</html>
