from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from login.views import set_run_info
from login.views import add_user_behavior
from login.auth import ExpiringTokenAuthentication
from rest_framework.decorators import action
from evaluate_bid import EvaluateBidSerializer
from tables import models


class EvaluateBidView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                      mixins.RetrieveModelMixin):
    """
    课题评审类
    """
    queryset = models.BidEvaluation.objects.all()
    authentication_classes = (ExpiringTokenAuthentication,)

    def get_serializer_class(self):
        if self.action == 'list':
            return EvaluateBidSerializer.EvaluateBidListSerializer
        elif self.action == 'create':
            return EvaluateBidSerializer.EvaluateBidCreateSerializer
        elif self.action == 'update':
            return EvaluateBidSerializer.EvaluateBidUpdateSerializer

    def create(self, request, *args, **kwargs):
        """
        专家评审
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        obj.operate_user = request.user
        obj.designated_experts = request.user.par
        obj.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        obj = serializer.save()
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(methods=['post'], detail=False)
    def create_many_items(self, request):
        """
        指定专家-同时创建多条
        :param request:
        :return:
        """
        param_dict = request.data
        print(param_dict)
        relate_bid_id = param_dict.get('relate_bid')  # 关联投标id
        designated_experts_list = param_dict.get('designated_experts_list')  # 研究人员id组成的列表
        try:
            relate_bid_obj = models.Bid.objects.get(pk=relate_bid_id)
            tmp_list = []
            for designated_experts_id in designated_experts_list:
                designated_experts_obj = models.Participant.objects.get(pk=designated_experts_id)
                tmp_obj = models.BidEvaluation(relate_bid=relate_bid_obj, designated_experts=designated_experts_obj)
                tmp_list.append(tmp_obj)
            models.BidEvaluation.objects.bulk_create(tmp_list)
            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='指定专家:{}'.format(relate_bid_id), user_obj=request.user)
            # -- 记录结束 --
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            set_run_info(level='error', address='/evaluae_bid/view.py/EvaluateBidView-create_many_items',
                         user=request.user.id, keyword='指定专家失败：{}'.format(e))
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=['get'], detail=False)
    def get_single_bid_experts_review_list(self, request):
        """
        获得单条投标的专家评审列表--阶段-立项
        :param request:
        :return:
        """
        param_dict = request.query_params
        relate_bid_id = param_dict.get('relate_bid')  # 关联投标id
        stage = param_dict.get('stage')  # 立项、中期、验收
        tag = param_dict.get('tag', 'info')  # 查看指定专家信息info或专家评审结果res
        try:
            query_list = models.BidEvaluation.objects.filter(relate_bid=relate_bid_id, stage=stage)
            print(query_list)
            if stage == "立项":
                if tag == 'info':
                    result = EvaluateBidSerializer.EvaluateBidParSerializer(instance=query_list, many=True)
                else:
                    result = EvaluateBidSerializer.EvaluateBidParReviewSerializer(instance=query_list, many=True)
            elif stage == "评审":
                return Response(status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='获得立项评审专家列表:{}-{}'.format(relate_bid_id, stage),
                              user_obj=request.user)
            # -- 记录结束 --
            return Response(result.data, status=status.HTTP_200_OK)
        except Exception as e:
            set_run_info(level='error', address='/evaluae_bid/view.py/EvaluateBidView-get_evaluation_experts_list',
                         user=request.user.id, keyword='获得立项评审专家列表失败：{}'.format(e))
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=['get'], detail=False)
    def get_experts_review_list(self, request):
        """
        获得专家评审列表
        :param request:
        :return:
        """
        param_dict = request.query_params
        relate_bid_id = param_dict.get('relate_bid')  # 关联投标id
        stage = param_dict.get('stage')  # 立项、中期、验收
        tag = param_dict.get('tag', 'info')  # 查看指定专家信息info或专家评审结果res
        try:
            query_list = models.BidEvaluation.objects.filter(relate_bid=relate_bid_id, stage=stage)
            print(query_list)
            if stage == "立项":
                if tag == 'info':
                    result = EvaluateBidSerializer.EvaluateBidParSerializer(instance=query_list, many=True)
                else:
                    result = EvaluateBidSerializer.EvaluateBidParReviewSerializer(instance=query_list, many=True)
            elif stage == "评审":
                return Response(status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='获得立项评审专家列表:{}-{}'.format(relate_bid_id, stage),
                              user_obj=request.user)
            # -- 记录结束 --
            return Response(result.data, status=status.HTTP_200_OK)
        except Exception as e:
            set_run_info(level='error', address='/evaluae_bid/view.py/EvaluateBidView-get_evaluation_experts_list',
                         user=request.user.id, keyword='获得立项评审专家列表失败：{}'.format(e))
            return Response(status=status.HTTP_404_NOT_FOUND)