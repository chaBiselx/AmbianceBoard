from home.utils.logger import LoggerFactory
import uuid
from home.models.ReportContent import ReportContent
from home.exceptions.PostDataException import PostDataException


class ReportContentService:
    
    def __init__(self, request):
        self.request = request
        self.logger = LoggerFactory.get_default_logger()
        
        
    def save_report(self):
        if(self.request.method == 'POST'):
       
            try:
                type_element = self.request.POST.get('element-type')
                uuid_element = self.request.POST.get('element-id')
                precision_element = self.request.POST.get('element-precision') or 'unknown'
                description_element = self.request.POST.get('element-description') or ''
                try:
                    uuid.UUID(uuid_element)
                except (ValueError, TypeError):
                    raise PostDataException(f"Faux UUID de contenu {{uuid_element: {uuid_element}}}")
            
                if(type_element and uuid_element and type_element in ['playlist', 'soundboard']):
                    
                    report = ReportContent.objects.create( typeElement=type_element, uuidElement=uuid_element, precisionElement=precision_element, descriptionElement=description_element)
                    if self.request.user.is_authenticated:
                        report.creator = self.request.user
                    report.save()
                    
                    # TODO envoyer un mail prioritaire au modérateur
                    return True
                else: 
                    raise PostDataException(f"Type de contenu ou uuid de contenu non renseigné {{type_element: {type_element}, uuid_element: {uuid_element}}}")
            except Exception as e:
                self.logger.error(e)
        return False
    
