# -*- coding: utf-8 -*-

import re
import os
import MySQLdb
import shutil
import pickle

import base_model

class Column_Chart(object):

    @classmethod
    def get_column_chart_javascript(self, ChartName, ContainerName, Title, Xaxis_name, Yaxis_title, DataStr, stacking='', SubTitle=''):
        char_javascript = '''
         var  __ChartName__ = new Highcharts.Chart({
            chart: {
                renderTo: '__ContainerName__',
                type: 'column'
            },
            title: {
                text: '__Title__'
            },
            subtitle: {
                text: '__SubTitle__'
            },
            xAxis: {
                categories: [__XAXIS_NAME__]
            },
            yAxis: {
                min: 0,
                title: {
                    text: '__YAXIS_TITLE__'
                }
            },
        '''
        if not stacking:
            char_javascript = char_javascript + '''
            legend: {
                layout: 'vertical',
                backgroundColor: '#FFFFFF',
                align: 'left',
                verticalAlign: 'top',
                x: 100,
                y: 70,
                floating: true,
                shadow: true
            },
        '''
        char_javascript = char_javascript + '''
            tooltip: {
                formatter: function() {
                    return ''+ this.series.name + "  " + 
                        /*this.x +*/': '+ this.y ;
                }
            },
            plotOptions: {
                column: {
                    stacking:'__STACKING__',
                    pointPadding: 0.2,
                    dataLabels: {
                        enabled: true
                        },
                    borderWidth: 0
                }
            },
                series: [__DATASTR__]
        });
        '''
        char_javascript = char_javascript.replace('__ChartName__',ChartName)
        char_javascript = char_javascript.replace('__ContainerName__',ContainerName)
        char_javascript = char_javascript.replace('__XAXIS_NAME__',Xaxis_name)
        char_javascript = char_javascript.replace('__YAXIS_TITLE__',Yaxis_title)
        char_javascript = char_javascript.replace('__Title__',Title)
        char_javascript = char_javascript.replace('__SubTitle__',SubTitle)
        char_javascript = char_javascript.replace('__STACKING__',stacking)
        char_javascript = char_javascript.replace('__DATASTR__',DataStr)
        return char_javascript

    @classmethod
    def get_column_Xaxis(self, str_dic):
        result = ''
        for a_key in str_dic.keys():
            a_list = [str(a_item )  for a_item in str_dic[a_key]]
            result = result + "{name:'" + a_key + "',data:[" + ",".join(a_list) + "]},"
        if result:
            result = result[0:-1]
        return result
        
        
    @classmethod
    def get_column_Xaxis_name(self, str_list):
        result = "'"
        if len(str_list)>0:
            result = result + "','".join(str_list) 
        result = result + " '"
        return result

    @classmethod
    def get_table_str(self, title_list, data_dic):
        result = '<table class="listing"><thead><tr><th></th>'
        my_column=0
        for a_key in data_dic:
            if len(data_dic[a_key])>my_column:
                my_column = len(data_dic[a_key])
        for a_item in range(my_column):
            result = result + '<th>' + title_list[a_item]  + '</th>' 
        result = result + '</thead>'
        for a_key in data_dic:
            a_list = data_dic[a_key]
            result = result + '<tr>'
            result = result + "<td>" + a_key+ "</td>"
            for a_item in a_list:
                result = result + "<td>" + str(a_item) + "</td>"
            result = result + '</tr>'
        result = result + "</table>"
        return result
        
