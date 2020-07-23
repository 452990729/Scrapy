#!/usr/bin/pyhton
# -*- coding: utf-8 -*-
from OMIMCrawler.items import OmimcrawlerItem
import re
from scrapy.http import Request
from scrapy.spiders import Spider


class OmimSpider(Spider):
    name = 'omimSpider'  # unique name
    allowed_domains = ['omim.org']
    start_urls = ['http://omim.org']

    def parse(self, response):
        """Loop each OMIM entry list in OMIM number file"""

        # http://omim.org/static/omim/data/mim2gene.txt
        mimnum_filename = '/home/lixuefei/Pipeline/Scrapy/OMIMCrawler/OMIMCrawler/mim2gene.txt'

        with open(mimnum_filename) as mimnum_file:
            for line in mimnum_file:
                if re.match('#', line):
                    continue
                mim_num = line.rstrip().split('\t')[0]  # omim number: e.g. 600185
                url = 'http://omim.org/entry/' + mim_num  # get OMIM entry
                print url
                # HTTP request the URL
                yield Request(url, method='GET', callback=self.parse_content)

    def parse_content(self, response):
        """Parse HTML content"""
        encode = 'utf-8'
        items = OmimcrawlerItem()
        items['omim_url'] = response.url

        content_selector = response.xpath('//div[@id="content"]/div[1]/div[2]/div[3]')

        # get related ICD+ information: SNOMEDCT, ORPHA, Disease Ontology
        icd_infos = content_selector.xpath('./div[1]/div[1]/div[1]/a/attribute::qtip_text').re(
            r'<strong>(.+):</strong>\s+(.+)<br/>')
        if icd_infos:
            for i in range(0, len(icd_infos), 2):
                if icd_infos[i] == 'SNOMEDCT':
                    items['snomedct_ids'] = icd_infos[i+1]  # encode(encode)
                elif icd_infos[i] == 'ORPHA':  # e.g. '329971, 2929'
                    items['orpha_ids'] = icd_infos[i+1]
                elif icd_infos[i] == 'DO':  # disease ontology
                    items['do_ids'] = icd_infos[i+1]

        # get OMIM id
        id_selector = content_selector.xpath('./div[1]/div[1]/div[2]/span/span')
        omim_id_strs = id_selector.xpath('.//text()').extract()
        omim_ids = []
        if omim_id_strs:
            for id_str in omim_id_strs:
                id_str = id_str.strip()
                if id_str:
                    omim_ids.append(id_str)
        if omim_ids:
            items['omim_id'] = ' '.join(omim_ids)  # e.g. '# 604370'


        # get OMIM name
        omim_name = content_selector.xpath('./div[1]/div[2]//span/text()').extract_first()
        if omim_name:
            items['omim_name'] = omim_name.strip()  # e.g. 'BREAST-OVARIAN CANCER, FAMILIAL, SUSCEPTIBILITY TO, 1; BROVCA1'

        # get Phenotype-Gene relationship
        table_heads = content_selector.xpath('./div[2]//table/thead/tr/th').extract()
        if table_heads:
            index_dict = {}
            # clean head string. e.g. u'<th>Phenotype <br> MIM number</th>'  ---->  u'Phenotype MIM number'
            table_heads = map(lambda x: re.sub('</?th>|<br>\s+', '', x), table_heads)
            # set table head names for Items object
            for i in range(len(table_heads)):
                if table_heads[i] == 'Location':
                    index_dict[i] = 'location'
                elif table_heads[i] == 'Phenotype':
                    index_dict[i] = 'phenotype'
                elif table_heads[i] == 'Phenotype MIM number':
                    index_dict[i] = 'phenotype_mim_number'
                elif table_heads[i] == 'Inheritance':
                    index_dict[i] = 'inheritance'
                elif table_heads[i] == 'Phenotype mapping key':
                    index_dict[i] = 'phenotype_mapping_key'
                elif table_heads[i] == 'Gene/Locus':
                    index_dict[i] = 'gene_locus'
                elif table_heads[i] == 'Gene/Locus MIM number':
                    index_dict[i] = 'gene_locus_mim_number'
       
            # Loop table lines
            for tr_selector in content_selector.xpath('./div[2]//table/tbody/tr'):  # for each row
                for i, td_selector in enumerate(tr_selector.xpath('./td')):  # for each column
                    td_items = td_selector.xpath('./span/*/text()').extract()
                    if not td_items:
                        td_items = td_selector.xpath('./span/text()').extract()
                    if td_items:
                        item = ', '.join(map(lambda x: x.strip(), td_items))
                        if items.get(index_dict[i]):
                            items[index_dict[i]].append(item)
                        else:
                            items[index_dict[i]] = [item]
        yield items
