class BaseDriver:
    async def nav_to_page(self, url):
        pass

    async def find_elements(self, selector):
        pass

    async def extract_metadata(self, elements):
        pass
    
    async def collect_downloads(self, elements):
        pass
    
    @property
    def closest_heading_expression(self):
        return """
            (node) => {
                let n = node;
                while (n) {
                    const h = n.querySelector('h1, h2, h3, h4, h5, h6, label')
                    if (h) return h.textContent;
                    n = n.parentNode;
                }
            }
        """    
