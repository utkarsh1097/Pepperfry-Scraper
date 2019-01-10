import scrapy
import os
import requests

category_list = ['two-seater-sofa','bench','book-cases','coffee-table','dining-set','queen-beds','arm-chairs','chest-drawers','garden-seating','bean-bags','king-beds']

start_url = 'https://www.pepperfry.com/site_product/search?q='
    
top_level = '../PepperFry_data/'

class MySpider(scrapy.Spider):
    name = "pepperfry"    

    def start_requests(self):
        
        os.makedirs(top_level, exist_ok = True)

        for category in category_list:
            os.makedirs(top_level+category, exist_ok = True)

            url = start_url + '+'.join(category.split('-'))
            yield scrapy.Request(url = url, headers = {'User-Agent':"Mozilla/5.0"}, meta = {'dont_redirect': False,'category': category}, dont_filter = True, callback = self.parse_category)

    def parse_category(self, response):
        cur_category = response.meta['category']

        item_path = top_level+cur_category 
        
        url_selector_list = response.css('#productView div.clip-dtl-ttl a::attr(href)').extract()

        item_url_list = [selector for selector in url_selector_list]

        #Looking for 20 items only
        for i in range(20):

            if item_url_list[i] is not None:
                
                cur_item_path =  item_path+"/Item"+str(i+1)+"/"
                
                os.makedirs(cur_item_path, exist_ok = True)

                yield response.follow(item_url_list[i], headers={'User-Agent':"Mozilla/5.0"}, meta = {'dont_redirect': False,'cur_item_path': cur_item_path}, dont_filter = True, callback = self.parse_item)

    def parse_item(self, response):
        
        cur_item_path = response.meta['cur_item_path']

        meta_file = cur_item_path + 'metadata.txt'

        item_heading = response.css('h1::text').extract_first() 
        
        item_details = response.css('#itemDetail p ::text').extract()


        image_url_list = response.css('.vip-options-slide a::attr(data-img)').extract()
        for i in range(len(image_url_list)):
            img_url = image_url_list[i]
            image = requests.get(img_url)
            image.raise_for_status()
            image_file = open(cur_item_path+"Image"+str(i+1)+".jpg", 'wb')
            for data_chunk in image.iter_content(100000):
                image_file.write(data_chunk)
            image.close()

        f = open(meta_file, 'w')
        f.write(item_heading+'\n')
        for i in range(len(item_details)):
            f.write(item_details[i]+'\n')
        f.close()
