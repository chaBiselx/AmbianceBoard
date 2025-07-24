import logging
from celery import shared_task
from django.apps import apps
from home.strategy.ReduceSizeImgStrategy import ReduceSizeImgStrategy

@shared_task
def reduce_size_img(model_name, model_id):
    logger = logging.getLogger('home')
    logger.info(f"reduce_size_img STARTED for {model_name} with id {model_id}")

    try:
        model_class = apps.get_model(app_label='home', model_name=model_name)
        model_instance = model_class.objects.get(pk=model_id)
    except Exception as e:
        logger.error(f"Could not retrieve model instance for {model_name} with id {model_id}: {e}")
        return False

    strategy_service = ReduceSizeImgStrategy()
    strategy = strategy_service.get_strategy(model_name)
    
    if strategy:
        strategy.resize(model_instance)
    else:
        logger.warning(f"No resize strategy found for model: {model_name}")
        
    logger.info("reduce_size_img ENDED")
    return True
