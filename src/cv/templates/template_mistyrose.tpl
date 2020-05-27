<html>
    <head>
        <meta charset="UTF-8">
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
        <script type="text/javascript">
            var autoSizeText;
            autoSizeText = function() {
              var el, elements, _i, _len, _results;
              elements = $('.resize');
              console.log(elements);
              if (elements.length < 0) {
                return;
              }
              _results = [];
              for (_i = 0, _len = elements.length; _i < _len; _i++) {
                el = elements[_i];
                _results.push((function(el) {
                  var resizeText, _results1;
                  resizeText = function() {
                    var elNewFontSize;
                    elNewFontSize = (parseInt($(el).css('font-size').slice(0, -2)) - 1) + 'px';
                    return $(el).css('font-size', elNewFontSize);
                  };
                  _results1 = [];
                  while (el.scrollHeight > el.offsetHeight) {
                    _results1.push(resizeText());
                  }
                  return _results1;
                })(el));
              }
              return _results;
            };
        </script>
        <style>
            * {
              margin: 0;
            }

            body {
              font-family: 'Montserrat', sans-serif;
            }

            .container {
              margin: 0 10%;
            }

            header {
              background-color: mistyrose;
              color: black;
              padding: 3%;
              margin-bottom: 70px;
              padding-right: 10%;
              padding-left: 10%;
              padding-top: 5%;
            }

            h2 {
              text-align: left;
              font-weight: 600;
              border-bottom: 1px solid grey;
              margin-top: 2rem;
              margin-bottom: 0.5rem;
            }

            #info {
                display: flow-root;
            }

            #name {
              font-size: 4.25rem;
              text-align: left;
              max-height: 120px;
              width: 600px;
              display: inline-block;
            }

            .item-name {
              font-weight: 600;
              margin-bottom: 0.5rem;
            }

            .item-date {
              font-weight: 200;
              margin-bottom: 0.5rem;
              text-align: right;
              float: right;
            }

            p {
              margin: 0;
              margin-top: 0.5rem;
            }

            .picture {
                width: 196px;
                height: 250px;
                display: inline-block;
                float: right;
            }

            .item {
              padding-bottom: 10px;
            }

            #klauzula {
              margin-top: 30px;
              margin-bottom: 30px;
              text-align: justify;
            }
        </style>
    </head>
    <body onload="autoSizeText()">
        <header>
            <div>
                {% if basic_info.picture %}<img class="picture" src="{{"../../usamo" + basic_info.picture.url}}"/>{% endif %}
            </div>
            <div id="info">
                <h1 id="name" class="resize">{{basic_info.first_name | escape}} {{basic_info.last_name | escape}}</h1>
                <div id="contact">
                    <p><b>Data urodzenia: </b></br>ur. {{basic_info.date_of_birth | escape}}</p>
                    <p><b>Telefon: </b></br>{{basic_info.phone_number | escape}}</p>
                    <p><b>E-mail: </b></br>{{basic_info.email | escape}}</p>
                </div>
            </div>
        </header>

        <div class="container" id="schools">
            <h2>Wykształcenie</h2>
            {% for item in schools %}
            <div class="item">
                <span class="item-name">{{item.name | escape}}</span>
                <span class="item-date">{{item.date_start | escape}} - {% if item.date_end %}{{item.date_end | escape}}{% else %}...{% endif %}</span>
                <p>{{item.additional_info | escape}}</p>
            </div>
            {% endfor %}
        </div>

        {% if experiences %}<div class="container" id="experiences">
            <h2>Doświadczenie</h2>
            {% for item in experiences %}
            <div class="item">
                <span class="item-name">{{item.title | escape}}</span>
                <span class="item-date">{{item.date_start | escape}} - {% if item.date_end %}{{item.date_end | escape}}{% else %}...{% endif %}</span>
                <p>{{item.description | escape}}</p>
            </div>
            {% endfor %}
        </div> {% endif %}

        <div class="container" id="skills">
            <h2>Umiejętności</h2>
            <p class="item">
                {% for item in skills %}
                {{item.description | escape}},
                {% endfor %}
            </p>
        </div>

        <div class="container" id="languages">
            <h2>Języki</h2>
            <p class="item">
                {% for item in languages %}
                {{item.name | escape}} - {{item.level | escape}},
                {% endfor %}
            </p>
        </div>

        <div class="container" id="klauzula">
            <p>
            Wyrażam zgodę na przetwarzanie moich danych osobowych dla potrzeb niezbędnych do realizacji
            procesu rekrutacji (zgodnie z ustawą z dnia 10 maja 2018 roku o ochronie danych osobowych 
            (Dz. Ustaw z 2018, poz. 1000) oraz zgodnie z Rozporządzeniem Parlamentu Europejskiego i Rady (UE) 
            2016/679 z dnia 27 kwietnia 2016 r. w sprawie ochrony osób fizycznych w związku z przetwarzaniem 
            danych osobowych i w sprawie swobodnego przepływu takich danych oraz uchylenia dyrektywy 95/46/WE (RODO)).
            </p>
        </div>
    </body>
</html>