{% if site.adsense_id %}
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={{ site.adsense_id}}" crossorigin="anonymous"></script>
{% endif %}

{% if site.ga_id %}
<script async src="https://www.googletagmanager.com/gtag/js/{{ site.ga_id }}"></script>
<script>
     window.dataLayer = window.dataLayer || [];
     function gtag(){dataLayer.push(arguments);}
     gtag('js', new Date());

     gtag('config', '{{ site.ga_id }}');
</script>
{% endif %}