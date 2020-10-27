from selenium.webdriver import Chrome, Edge, Firefox, Ie, PhantomJS, Safari


ChromeDriver = lambda path, *args, **kwargs: lambda: Chrome(path, *args, **kwargs)
EdgeDriver = lambda path, *args, **kwargs: lambda: Edge(path, *args, **kwargs)
FirefoxDriver = lambda path, *args, **kwargs: lambda: Firefox(*args, executable_path=path, **kwargs)
IeDriver = lambda path, *args, **kwargs: lambda: Ie(path, *args, **kwargs)
PhantomJSDriver = lambda path, *args, **kwargs: lambda: PhantomJS(path, *args, **kwargs)
SafariDriver = lambda path, *args, **kwargs: lambda: Safari(path, *args, **kwargs)
