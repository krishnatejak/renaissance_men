from exc import handle_exceptions
from utils import allow
from admin.handlers.common import BaseHandler
from admin.service.serviceprovider import *
from admin.service.order import get_sp_orders_by_status
from admin.service.order import get_sp_order_bids
from tornado.gen import coroutine
import tornado.httpclient
import tornado.web


from botocore_tornado import session as botosession
__all__ = ['ServiceProviderHandler', 'ServiceProviderJobHandler',
           'ServiceProviderOrdersHandler', 'ServiceProviderUploadHandler',
           'AdminServiceProviderHandler', 'ServiceProviderBidsHandler']


class ServiceProviderHandler(BaseHandler):
    resource_name = 'serviceprovider'
    create_required = {'email', 'phone_number'}
    update_ignored = {'service', 'id', 'created'}

    @handle_exceptions
    @allow('service_provider', base=True)
    def put(self, *args, **kwargs):
        data = self.check_input('update')
        service_provider = update_service_provider(
            self.dbsession, kwargs['pk'], data
        )
        self.send_model_response(service_provider, follow=True)

    @handle_exceptions
    @allow('service_provider', base=True)
    def get(self, *args, **kwargs):
        service_provider = get_service_provider(self.dbsession, kwargs['pk'])
        self.send_model_response(service_provider, follow=True)


class ServiceProviderJobHandler(BaseHandler):

    @handle_exceptions
    @allow('service_provider', base=True)
    def get(self, *args, **kwargs):
        status = self.get_argument("status", "")
        jobs = fetch_jobs_by_status(self.dbsession, kwargs['pk'], status)
        self.send_model_response(jobs)


class ServiceProviderOrdersHandler(BaseHandler):
    #TODO evaluate if follow is required for this api
    @handle_exceptions
    @allow('service_provider', base=True)
    def get(self, *args, **kwargs):
        status = self.get_argument("status", "")
        orders = get_sp_orders_by_status(self.dbsession, kwargs['pk'], status)
        self.send_model_response(orders)


class ServiceProviderUploadHandler(BaseHandler):
    """
    Photo,
    Aadhar Card,
    Voter ID,
    DL,
    ITI Certificate,
    Police Background
    """
    file_fields = ('photo', 'dl', 'pan', 'aadhar', 'voter', 'iti', 'police')

    @coroutine
    @handle_exceptions
    @allow('service_provider', 'admin', base=True, post_pk=True)
    def post(self, *args, **kwargs):

        service_provider = get_service_provider(self.dbsession, kwargs['pk'])

        files = self.get_files()
        session = botosession.get_session()
        s3 = session.get_service('s3')
        endpoint = s3.get_endpoint('us-west-2')
        operation = s3.get_operation('PutObject')
        bucket = 'sevame'
        operations = {}

        for document_type, data in files.iteritems():
            key = 'documents/sp_{}_{}.{}'.format(
                service_provider.id,
                document_type,
                data['ext']
            )
            operations[document_type] = operation.call(
                endpoint,
                bucket=bucket,
                key=key,
                body=open(data['path'], 'rb')
            )
        try:
            response_dict = yield operations

            for document_type in response_dict:
                response, response_data = response_dict[document_type]
                service_provider.details[document_type + '_link'] = response.effective_url

            self.dbsession.add(service_provider)
            self.dbsession.commit()

            self.send_model_response(service_provider, follow=True)

        except tornado.httpclient.HTTPError as e:
            print 'upload failed %s' % e
            self.set_status(400)
            self.write({'error': 'unable to upload, please try again later'})

    def get_files(self):
        """returns uploaded file data
            request arguments format
        {
            u'fileUpload1.name': ['Screen Shot 2014-06-20 at 6.27.32 PM.png'],
            u'fileUpload1.md5': ['5936dc20d2f807ca643d819061934a00'],
            u'fileUpload1.content_type': ['image/png'],
            u'fileUpload1.size': ['483593'],
            u'fileUpload1.path': ['/tmp/uploads/0000000016']
        }
        """

        arguments = self.request.arguments

        document_types = set([
            key.split('.')[0]
            for key in self.request.arguments
        ])
        files = {}
        for document_type in document_types:
            if document_type in self.file_fields:
                files[document_type] = {
                    'path': arguments[document_type + '.path'][0],
                    'content_type': arguments[document_type + '.content_type'][0],
                    'ext': arguments[document_type + '.name'][0].split('.')[-1]
                }
            else:
                print 'invalid document type %s' % document_type
        return files


class AdminServiceProviderHandler(ServiceProviderHandler):

    @handle_exceptions
    @allow('admin')
    def post(self, *args, **kwargs):
        data = self.check_input('create')
        service_provider = create_service_provider(self.dbsession, data)
        self.send_model_response(service_provider, follow=True)

    @handle_exceptions
    @allow('admin')
    def put(self, *args, **kwargs):
        data = self.check_input('update')
        service_provider = update_service_provider(
            self.dbsession, kwargs['pk'], data
        )
        self.send_model_response(service_provider, follow=True)

    @handle_exceptions
    @allow('admin', allow_list=True)
    def get(self, *args, **kwargs):
        if kwargs['pk']:
            kwargs['pk'] = kwargs['pk'].strip('/')
        service_provider = get_service_provider(self.dbsession, kwargs['pk'])
        self.send_model_response(service_provider, follow=True)

    @handle_exceptions
    @allow('admin')
    def delete(self, *args, **kwargs):
        pass


class ServiceProviderBidsHandler(BaseHandler):

    @allow('service_provider', base=True)
    def get(self, *args, **kwargs):
        order_bids = get_sp_order_bids(self.dbsession, kwargs['uid'])
        self.send_model_response(order_bids)