# vastplace_example_module

This project is an example module for the [vastplace](https://github.com/tkerdonc/vastplace) project. It demonstrates its capabilities by parsing a .csv file containing GPS and dummy measurements.

## Getting Started

### Installing

This install assumes that you already have a vastplace install in ~/src/vastenv/vastplace
We will now create a working copy of this vastplace module, and enable it in vastplace.

```
cd src
git clone https://github.com/tkerdonc/vastplace_example_module.git
cd vastenv/vastplace/experiments
ln -s ../../../vastplace_example_module vastplace_example_module
cd ..
```

This linked the example module sources to a local folder of vastplace, we now need to enable it :

<pre>
vim centraldb/settings.py
</pre>

and add
<pre>
'experiments.vastplace_example_module'
</pre>
 to the *INSTALLED_APPS* entry
We also need to route the urls to the example module :

<pre>
vim centraldb/urls.py
</pre>

and add
<pre>
url(r'^vastplace_example_module/', include('experiments.vastplace_example_module.urls')),
</pre>

to the *urlpatterns* entry.

the example module should now be enabled.

## Uploading a trace

This module parses csv traces with the following format, and separated by tabs.
the metal entries emulate an hypothetic sensor.

```
timestamp	GPS	latitude	longitude
timestamp	metal	value
```

Navigate to the following url, and use the trace upload form.
<pre>
/campaignfiles/content
</pre>

Once the trace uploaded, you are prompted with the detail filling form. You must pick the *vastplace_example* format. Once saved, a map will be plotted.
you can then navigate to the *Example* tab for a short description of the features of the platform

## Features

This module exposes its features via the following URLs :

|URL                                 | Type |Description                                   |
|------------------------------------|------|----------------------------------------------|
|vastplace_example/                  | HTML | Index                                        |
|vastplace_example/tile_map          | HTML | Map of all traces                            |
|vastplace_example/cell_map          | HTML | Geographic cell processing                   |


## License
This project is licensed under the BSD 3 License - see the [LICENSE.md](LICENSE.md) file for details
