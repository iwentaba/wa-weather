(function($, L, window, document) {

    var date;
    var status_bar;
    var rain_plot;
    var map;

    $(function() {
        status_bar = StatusBar();
        rain_plot = RainPlot();
        map = Map(-32, 115.76);
        date = DateSelector(new Date());

        date.add_change_listener(function(new_date) {
            refresh();
        });

        map.add_click_listeners(function(lat, lon) {
            refresh();
        });

        refresh();
    })

    function refresh() {
        fetch_rain($("#date").val(), map.lat, map.lon, function(data) {
            rain_plot.update(data);
            map.plot_bounds(data.bounds, data.boundary);
            status_bar.update(data.last_updated)
        });
    }

    function fetch_rain(date,lat,lon,success) {
        $.ajax("/getRain", {
            data: {
                date:date,
                lat:lat,
                lon:lon
            },
            success: success
        })
    }

    function Map(init_lat, init_lon) {
        var map_bounds;
        var map;
        var marker;
        var lat;
        var lon;
        var click_listeners = [];
        var id = "map";

        map = L.map(id).setView([init_lat, init_lon], 13);
        set_lat_lon(init_lat, init_lon);

        let osm_map = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        });
        osm_map.addTo(map);

        map.on('click', function(e) {
            for (f of click_listeners) {
                 f(e.latlng.lat, e.latlng.lng);
            }
        });

        add_click_listeners(function(new_lat, new_lon) {
            set_lat_lon(new_lat, new_lon);
        });

        var plot_bounds = function(geojson, boundary) {
            if (map_bounds) {
                map.removeLayer(map_bounds);
            }

            var bound_style = {
                "color": "#41ee90",
                "weight": 5,
                "opacity": 0.8
            };
            map_bounds = new L.GeoJSON(geojson, bound_style);
            map_bounds.addTo(map);
        };

        function set_lat_lon(new_lat,new_lon) {
            lat = new_lat;
            lon = new_lon;
            if (marker == null) {
                marker = L.marker([lat, lon]).addTo(map);
            } else {
                marker.setLatLng([lat,lon]);
            }
        };

        // f: function(lat,lon)
        function add_click_listeners(f) {
            click_listeners.push(f);
        };

        return {"plot_bounds": plot_bounds,
                "add_click_listeners": add_click_listeners,
                "set_lat_lon": set_lat_lon,
                "lat": lat,
                "lon": lon
        };
    }

    function RainPlot() {
        var id = "#rain_plot";
        // Expects {"data":[{"t":time, "r":rain}.., ], "max_rain": }
        function update(data) {
            data.data = data.data.map(function(x) {
                return {"t": new Date(x.t*1000), "r":x.r};
            });
            return MG.data_graphic({
                description: "Rain(mm/h)",
                data: data.data,
                area: true,
                target: id,
                baselines: [{"value": 2.5, "label": "light"},
                            {"value": 20, "label": "moderate"},
                            {"value": 100, "label": "heavy"},],
                markers: [{"t": new Date(), "label": "now"
                }],
                x_accessor: 't',
                y_accessor: 'r',
                x_label: 'time',
                y_label: 'rain(mm/h)',
                max_y: data.max_rain,
                full_height: true,
                full_width: true,
                top: 20,
            });
        };
        return {"update": update};
    }

    function DateSelector(initial_date) {
        var change_listeners = [];
        var date_input = $("#date");
        date_input.val(print_date(initial_date));
        date_input.attr({min: print_date(add_days(initial_date,-20)), max: print_date(add_days(initial_date,5))});

        date_input.on("change",function() {
            for (f of change_listeners) {
                f();
            }
        });

        function print_date(date) {
            return `${date.getFullYear()}-${int_to_str(date.getMonth()+1,2)}-${int_to_str(date.getDate(),2)}`;
        }

        function int_to_str(int, padn=0) {
            return `${int}`.padStart(padn,"0");
        }

        function add_days(date, days) {
            return new Date(date.valueOf() + days*24*3600*1000);
        }

        // f: function(date)
        var add_change_listener = function(f) {
            change_listeners.push(f);
        }

        return {"add_change_listener" : add_change_listener};
    }

    function StatusBar() {
        var id = $("#status");

        var update = function(date_millis) {
            id.text("Last updated: " + new Date(date_millis))
        };

        return {"update": update};
    }

}(window.jQuery, window.L, window, document));